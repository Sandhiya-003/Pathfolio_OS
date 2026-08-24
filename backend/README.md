# Pathfolio — Backend

FastAPI backend for **Pathfolio**, an AI-powered Digital Identity System. Ingests documents
(certificates, resumes, project reports, internship letters), classifies and organizes them
automatically, links related skills/projects/internships into a knowledge graph, and answers
natural-language questions about them.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Copy the environment template and fill it in:

```bash
cp .env.example .env
```

`.env`:
```
JWT_SECRET_KEY=<a long random string>
GEMINI_API_KEY=<your key from https://aistudio.google.com/app/apikey>
GEMINI_MODEL=gemini-3.7-flash
```

`JWT_SECRET_KEY` is required (accounts won't work without it). `GROQ_API_KEY` is optional —
every feature except the "Ask your archive" chat assistant works without it; the chat endpoint
returns a clear `503` telling you it isn't configured until you add a key.

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create a Gemini API key in **Google AI Studio**.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Docs at `http://localhost:8000/docs`. Health check: `curl http://localhost:8000/health`.

## Run tests

```bash
pytest tests/ -v
```

These are integration tests against the real app (register a throwaway user, upload a sample
document, hit every endpoint). The Gemini-dependent test mocks the LLM call, so the suite runs
without an API key or network access.

## Architecture

```
app/
  main.py                    # FastAPI app, lifespan startup, error handlers
  core/                      # config, logging, constants, JWT/password security
  api/
    routes/                  # one router per feature: auth, upload, search, documents,
                              # timeline, relationships, insights, chat
    deps.py                  # get_current_user / get_current_user_id (JWT auth)
  services/                  # business logic (one class + one singleton per file)
    upload_service.py        # orchestrates the ingestion pipeline
    classification_service.py # category classification, delegates to ai/extractors/
    summarization_service.py # extractive summary -> document description
    vector_service.py        # embeddings + semantic search (ChromaDB)
    relationship_service.py  # builds the skill/document knowledge graph
    timeline_service.py      # groups documents into a yearly timeline
    insight_service.py       # profile score, skill gaps, growth metrics
    chat_service.py          # RAG: retrieval_service + Groq chat completion
    auth_service.py          # register/login/password hashing
  ai/
    extractors/               # date/entity/skill extraction (spaCy + regex)
    pipelines/                 # ingestion/relationship/retrieval pipelines
  db/
    sqlite_db.py              # documents, relationships, skills, users
    chroma_db.py               # vector store client
    repositories/               # narrow per-entity data-access wrappers
  models/                     # internal Pydantic domain models
  schemas/                    # API request/response DTOs
tests/                        # pytest suite (see conftest.py for fixtures)
```

## Auth

Every route except `/auth/register`, `/auth/login`, and `/health` requires a
`Authorization: Bearer <token>` header. Each user only ever sees, searches, and chats over
their own documents — enforced server-side on every route, not just hidden in the UI.

## The RAG assistant

`POST /api/chat/` takes `{"message": "...", "history": [...]}`, retrieves the most relevant
documents for that user via the existing semantic search, feeds them to Groq as context, and
returns `{"answer": "...", "sources": [...]}` — the source documents are the ones the model was
actually given, not a separate "related docs" guess, so citations are always accurate to what
the model saw.
