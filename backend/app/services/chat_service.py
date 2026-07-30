SYSTEM_PROMPT = """You are the Pathfolio Assistant, a helpful guide to a student's personal \
digital archive of certificates, projects, internships, and achievements.

Answer the user's question using ONLY the documents provided below as context. If the answer \
isn't in the context, say so honestly instead of guessing.

When asked about skills, technologies, or details "from these" or "from that" documents, look at \
the Skills line for each document in the context below and answer with the actual skill names \
directly -- do not just restate the document titles again. Be specific: list the skills, don't \
describe where to find them.

Reference documents by their title when it's helpful. Keep answers concise and conversational -- \
this is a chat, not a report.

DOCUMENTS FROM THE USER'S ARCHIVE:
{context}
"""

import time
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logger import logger
from app.services.retrieval_service import retrieval_service

SYSTEM_PROMPT = """You are the Pathfolio Assistant, a helpful guide to a student's personal \
digital archive of certificates, projects, internships, and achievements.

Answer the user's question using ONLY the documents provided below as context. If the answer \
isn't in the context, say so honestly instead of guessing. Reference documents by their title \
when it's helpful. Keep answers concise and conversational -- this is a chat, not a report.

DOCUMENTS FROM THE USER'S ARCHIVE:
{context}
"""

NO_CONTEXT_NOTE = "No matching documents were found in this user's archive for this question."


class ChatServiceError(Exception):
    """Raised for expected chat failures (missing key, upstream error) -- safe to show to the user."""


class ChatService:
    """Answers natural-language questions about a user's archive using Groq + retrieval."""

    def __init__(self):
        self.retrieval = retrieval_service
        self._client = None

    def _get_client(self):
        if not settings.GROQ_API_KEY:
            return None
        if self._client is None:
            self._client = groq(api_key=settings.GROQ_API_KEY)
        return self._client

    def _build_context(self, results: List[Dict]) -> str:
        if not results:
            return NO_CONTEXT_NOTE

        blocks = []
        for i, r in enumerate(results, 1):
            skills = ", ".join(r.get("skills", [])) or "none listed"
            blocks.append(
                f"[{i}] Title: {r['title']}\n"
                f"Category: {r['category']}\n"
                f"Date: {r.get('date') or 'unknown'}\n"
                f"Skills: {skills}\n"
                f"Excerpt: {r['snippet']}"
            )
        return "\n\n".join(blocks)

    def _build_retrieval_query(self, message: str, history: Optional[List[Dict]]) -> str:
        """
        Combine the current message with the last user/assistant turn so
        follow-ups like "skills detected from these" retrieve the same
        documents as the turn they're referring to, instead of searching
        on "skills detected from these" alone (which matches nothing).
        """
        if not history:
            return message

        recent = history[-2:]  # last user + last assistant turn, if present
        context_snippets = [turn["content"] for turn in recent]
        return " ".join(context_snippets + [message])

    def ask(self, message: str, user_id: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Answer `message` using retrieval-augmented generation over this user's documents.

        Raises ChatServiceError for expected, user-facing failures (no API key configured,
        upstream Groq error) so the route can turn it into a clean HTTP error.
        """
        start = time.time()

        client = self._get_client()
        if not client:
            raise ChatServiceError(
                "The assistant isn't configured yet -- add a GROQ_API_KEY to the backend's .env file."
            )

        retrieval_query = self._build_retrieval_query(message, history)
        search_results = self.retrieval.search(
            retrieval_query, filters={"user_id": user_id}, limit=settings.CHAT_CONTEXT_DOCS
        )
        results = search_results["results"]
        context_block = self._build_context(results)

        messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context_block)}]
        for turn in (history or [])[-10:]:  # cap history for token budget
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})

        try:
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
            )
            answer = completion.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Groq chat completion failed: {e}")
            raise ChatServiceError("The assistant is temporarily unavailable. Please try again.")

        sources = [
            {
                "document_id": r["document_id"],
                "title": r["title"],
                "category": r["category"],
                "date": r.get("date"),
                "similarity_score": r["similarity_score"],
            }
            for r in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "used_context": len(results) > 0,
            "processing_time_ms": round((time.time() - start) * 1000, 2),
        }


# Singleton instance
chat_service = ChatService()
