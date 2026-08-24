"""RAG chat assistant, powered by the Gemini API."""

import time
from typing import Dict, List, Optional

import httpx
from app.core.config import settings
from app.core.logger import logger
from app.services.retrieval_service import retrieval_service

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

NO_CONTEXT_NOTE = "No matching documents were found in this user's archive for this question."


class ChatServiceError(Exception):
    """Raised for expected chat failures (missing key, upstream error) -- safe to show to the user."""


class ChatService:
    """Answers natural-language questions about a user's archive using Gemini + retrieval."""

    def __init__(self):
        self.retrieval = retrieval_service
        self._client = None

    def _get_client(self):
        if not settings.GEMINI_API_KEY:
            return None
        if self._client is None:
            self._client = httpx.Client(timeout=30.0)
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
        """Fold recent conversation into the search query so follow-ups like
        "skills detected from these" retrieve the same documents as the turn
        they're referring to, instead of searching on those words alone."""
        if not history:
            return message
        recent = history[-2:]
        context_snippets = [turn["content"] for turn in recent]
        return " ".join(context_snippets + [message])

    @staticmethod
    def _gemini_contents(message: str, history: Optional[List[Dict]]) -> List[Dict]:
        """Translate the app's user/assistant history to Gemini's user/model roles."""
        contents = [
            {
                "role": "model" if turn["role"] == "assistant" else "user",
                "parts": [{"text": turn["content"]}],
            }
            for turn in (history or [])[-10:]
        ]
        contents.append({"role": "user", "parts": [{"text": message}]})
        return contents

    @staticmethod
    def _response_text(payload: Dict) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()

    def ask(self, message: str, user_id: str, history: Optional[List[Dict]] = None) -> Dict:
        start = time.time()

        client = self._get_client()
        if not client:
            raise ChatServiceError(
                "The assistant isn't configured yet -- add a GEMINI_API_KEY to the backend's .env file."
            )

        retrieval_query = self._build_retrieval_query(message, history)
        search_results = self.retrieval.search(
            retrieval_query, filters={"user_id": user_id}, limit=settings.CHAT_CONTEXT_DOCS
        )
        results = search_results["results"]
        context_block = self._build_context(results)

        try:
            response = client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{settings.GEMINI_MODEL}:generateContent",
                headers={"x-goog-api-key": settings.GEMINI_API_KEY},
                json={
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT.format(context=context_block)}]},
                    "contents": self._gemini_contents(message, history),
                    "generationConfig": {
                        "temperature": settings.GEMINI_TEMPERATURE,
                        "maxOutputTokens": settings.GEMINI_MAX_TOKENS,
                    },
                },
            )
            response.raise_for_status()
            answer = self._response_text(response.json())
            if not answer:
                raise ChatServiceError("Gemini returned no response text.")
        except ChatServiceError:
            raise
        except Exception as e:
            logger.error(f"❌ Gemini chat completion failed: {e}")
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


chat_service = ChatService()
