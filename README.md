<div align="center">

# 🗂️ Pathfolio

### Your Digital Identity, Organized by AI

*Certificates. Resumes. Project reports. Internship letters. Every document you've ever earned —
automatically read, classified, connected, and made instantly searchable.*

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_search-8A2BE2?style=flat)](https://www.trychroma.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

</div>

---

## The problem

Every student builds a digital footprint across years of academic and professional life —
certificates, resumes, project reports, internship letters, GitHub repos, achievements. Yet all
of it sits scattered across folders, emails, and cloud drives. Storage platforms can *hold* those
files. None of them *understand* the story those files tell.

**Pathfolio is not another cloud drive.** It's an AI layer that reads what you upload, figures out
what it is, connects it to everything else you've built, and lets you ask for it back in plain
English — *"show me my AI projects,"* *"what certificates do I have,"* *"summarize my internship
experience."*

---

## ✨ What it actually does

| Module | What happens |
|---|---|
| **🧠 AI Ingestion** | Drop in a PDF, DOCX, image, or text file. Text is extracted (with OCR fallback for scanned documents), and the pipeline reads it — no manual tagging, no folders to choose. [...]
| **🏷️ Intelligent Categorization** | A classification engine scores the document against category signatures and files it under Certification, Project, Internship, Achievement, Academic, Resume,[...]
| **🕸️ Relationship Engine** | Every document is linked to the skills it mentions, and skills are linked across documents — a Python certificate connects to the Python project it enabled, which[...]
| **📜 Digital Journey Timeline** | Documents are automatically grouped by the year extracted from their content, turning a folder of files into a visual career timeline: *2023 → Python Certificat[...]
| **🔍 Smart Retrieval** | Semantic search (sentence-transformer embeddings + ChromaDB) means *"AI projects"* finds a document titled "Intelligent Traffic System" even though those exact words never[...]
| **💬 Ask Your Archive** | A retrieval-augmented chat assistant (Groq / Llama 3.3 70B) that answers questions about your own documents in natural language and cites exactly which ones it used — n[...]
| **📊 Career Insights** | A profile completeness score, skill-strength analysis (emerging → developing → strong), skill-gap recommendations, year-over-year growth metrics, and AI-generated high[...]

Every file stays accessible in its **original format** — nothing is locked away or converted. Every
feature above is scoped to the signed-in user; one account can never see another's documents,
enforced at the database layer, not just hidden in the UI.

---

## 🖥️ Screenshots

> *Add screenshots or a demo GIF here — Dashboard, Ingest, Knowledge Map, and the Ask assistant
> make the strongest impression.*
