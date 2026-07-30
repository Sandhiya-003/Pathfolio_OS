# Pathfolio — Frontend

The frontend for **Pathfolio**, an AI-powered Digital Identity System. Built with React + Vite +
Tailwind CSS, talking to the FastAPI backend in `backend/`.

## Auth

Pathfolio now has real accounts. `/login` and `/signup` are public; everything else redirects
to `/login` if you don't have a valid session. The JWT is stored in `localStorage` and attached
to every API call automatically (see `src/lib/api.js`). Each user only ever sees their own
documents, timeline, and knowledge graph — enforced on the backend, not just hidden in the UI.

## What's here

| Route            | Module                        | What it does                                                        |
|-------------------|-------------------------------|-----------------------------------------------------------------------|
| `/`                | Dashboard                     | Stats, AI highlights, recently ingested documents                    |
| `/upload`          | Module 1 — AI Data Ingestion  | Drag-and-drop multi-file upload with live classification feedback    |
| `/documents`       | Module 2 — Categorization     | Full archive, filterable by category, with original-file download    |
| `/search`          | Module 5 — Smart Retrieval    | Natural-language search ("show my AI projects")                      |
| `/timeline`        | Module 4 — Digital Journey    | Vertical timeline of your growth, grouped by year                    |
| `/relationships`   | Module 3 — Relationship Engine| Radial knowledge graph connecting skills ↔ documents                 |
| `/insights`        | AI career layer               | Profile score, skill strength, gap analysis, growth chart, skill-journey tracer |
| `/login`, `/signup` | Auth                           | Sign in / create an account                                          |

## 1. Prerequisites

- Node.js 18+ and npm
- The Pathfolio backend running locally (see `backend/`) — by default at `http://localhost:8000`

## 2. Setup

```bash
cd frontend
npm install
```

Copy the example env file and point it at your backend:

```bash
cp .env.example .env
```

`.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

## 3. Run the backend (in a separate terminal)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

Confirm it's up: `curl http://localhost:8000/health`

## 4. Run the frontend

```bash
npm run dev
```

Open the printed URL (typically `http://localhost:5173`).

## 5. Build for production

```bash
npm run build     # outputs to dist/
npm run preview   # serve the production build locally
```

## Project structure

```
src/
  lib/
    api.js              # single client wrapping every backend endpoint
    categories.js        # category -> emoji/color, mirrors backend's category_mapper.py
  context/
    ToastContext.jsx     # global toast notifications
  components/
    Sidebar.jsx, TopBar.jsx          # navigation
    DocumentCard.jsx, DocumentModal.jsx
    CategoryBadge.jsx, StatCard.jsx, EmptyState.jsx, Loader.jsx
  pages/
    Dashboard.jsx, Upload.jsx, Documents.jsx,
    Search.jsx, Timeline.jsx, Relationships.jsx, Insights.jsx
```

## Notes

- All API calls live in `src/lib/api.js`. If you change a backend route, that's the only file
  that needs updating.
- CORS: the backend's `ALLOWED_ORIGINS` setting must include your frontend's dev URL
  (`http://localhost:5173` by default) — check `backend/app/core/config.py`.
- Uploaded files stay in their original format on the server; every card and the document modal
  link straight to `GET /api/documents/{id}/download`.
