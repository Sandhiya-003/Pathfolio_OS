"""
INGESTION PIPELINE
==================
Orchestrates the complete AI document processing workflow:

    ┌──────────┐   ┌───────────┐   ┌──────────────┐   ┌────────────┐   ┌───────────────┐
    │  File    │──▶│  Extract  │──▶│  Understand  │──▶│   Embed    │──▶│    Connect    │
    │  Upload  │   │  (OCR/    │   │  (NER, NLP,  │   │  (Vector   │   │ (Relationship │
    │          │   │   Parse)  │   │   Classify)  │   │   Store)   │   │    Engine)    │
    └──────────┘   └───────────┘   └──────────────┘   └────────────┘   └───────────────┘

Every stage is logged, timed, and returns explainable output —
this is what makes the system "understand" a document, not just store it.
"""

import os
import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.extraction_service import extraction_service
from app.services.classification_service import classification_service
from app.services.vector_service import vector_service
from app.services.relationship_service import relationship_service
from app.db.sqlite_db import sqlite_db
from app.utils.text_cleaner import clean_text
from app.core.logger import logger


class IngestionPipeline:
    """End-to-end AI ingestion pipeline for uploaded documents."""

    def __init__(self):
        self.extractor = extraction_service
        self.classifier = classification_service
        self.vector = vector_service
        self.relationships = relationship_service
        self.db = sqlite_db

    def run(self, file_path: str, original_filename: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Execute the full ingestion pipeline on a single document.

        Returns a rich, explainable result showing every AI stage —
        perfect for demoing "the system understood my document."
        """
        pipeline_start = time.time()
        doc_id = str(uuid.uuid4())
        stages = {}  # Track timing + output of every stage for explainability

        logger.info(f"🔄 [PIPELINE] Starting ingestion for: {original_filename}")

        # ─────────────────────────────────────────────
        # STAGE 1: TEXT EXTRACTION (PDF / DOCX / OCR)
        # ─────────────────────────────────────────────
        stage_start = time.time()
        extraction = self.extractor.extract(file_path)
        raw_text = extraction.get("text", "")

        if not raw_text.strip():
            return self._fail(doc_id, original_filename, "No extractable text found in document")

        cleaned_text = clean_text(raw_text)
        stages["extraction"] = {
            "duration_ms": self._ms(stage_start),
            "file_type": extraction.get("file_type"),
            "word_count": extraction.get("word_count", 0),
            "pages": extraction.get("pages", 1),
        }
        logger.info(f"   ✅ Stage 1/5 Extraction: {stages['extraction']['word_count']} words")

        # ─────────────────────────────────────────────
        # STAGE 2: UNDERSTANDING (NER + Classification)
        # ─────────────────────────────────────────────
        stage_start = time.time()
        understanding = self.classifier.process_document(cleaned_text, original_filename)

        stages["understanding"] = {
            "duration_ms": self._ms(stage_start),
            "category": understanding["category"],
            "confidence": understanding["confidence"],
            "skills_found": understanding["skills"],
            "organizations": understanding["organizations"],
            "date_detected": understanding["primary_date"],
        }
        logger.info(
            f"   ✅ Stage 2/5 Understanding: category='{understanding['category']}' "
            f"({understanding['confidence']:.0%} confidence), "
            f"{len(understanding['skills'])} skills"
        )

        # ─────────────────────────────────────────────
        # STAGE 3: PERSISTENCE (Original file preserved)
        # ─────────────────────────────────────────────
        stage_start = time.time()
        document = {
            "id": doc_id,
            "user_id": user_id,
            "title": understanding["title"],
            "category": understanding["category"],
            "file_type": os.path.splitext(original_filename)[1].lstrip("."),
            "file_path": file_path,
            "original_filename": original_filename,
            "extracted_text": cleaned_text,
            "skills": understanding["skills"],
            "organizations": understanding["organizations"],
            "date_extracted": understanding["primary_date"],
            "description": f"Auto-classified via AI (confidence: {understanding['confidence']:.0%})",
            "embedding_id": doc_id,
        }
        self.db.insert_document(document)
        stages["persistence"] = {"duration_ms": self._ms(stage_start)}
        logger.info(f"   ✅ Stage 3/5 Persistence: metadata + original file saved")

        # ─────────────────────────────────────────────
        # STAGE 4: EMBEDDING (Semantic vector generation)
        # ─────────────────────────────────────────────
        stage_start = time.time()
        # Compose enriched text: title + skills + content = better semantic search
        enriched_text = (
            f"{understanding['title']}. "
            f"Category: {understanding['category']}. "
            f"Skills: {', '.join(understanding['skills'])}. "
            f"{cleaned_text[:4000]}"
        )
        self.vector.add_document(
            doc_id=doc_id,
            text=enriched_text,
            metadata={
                "title": understanding["title"],
                "category": understanding["category"],
                "skills": ",".join(understanding["skills"]),
                "user_id": user_id,
                "date": understanding["primary_date"] or "",
            },
        )
        stages["embedding"] = {
            "duration_ms": self._ms(stage_start),
            "model": "all-MiniLM-L6-v2",
            "dimensions": 384,
        }
        logger.info(f"   ✅ Stage 4/5 Embedding: 384-dim vector stored in ChromaDB")

        # ─────────────────────────────────────────────
        # STAGE 5: KNOWLEDGE CONNECTIONS (Relationship Engine)
        # ─────────────────────────────────────────────
        stage_start = time.time()
        relationship_ids = self.relationships.build_relationships(doc_id, understanding)
        stages["relationships"] = {
            "duration_ms": self._ms(stage_start),
            "connections_created": len(relationship_ids),
        }
        logger.info(f"   ✅ Stage 5/5 Relationships: {len(relationship_ids)} connections built")

        total_time = round(time.time() - pipeline_start, 2)
        logger.info(f"🎉 [PIPELINE] Complete in {total_time}s → {doc_id}")

        return {
            "success": True,
            "document_id": doc_id,
            "filename": original_filename,
            "title": understanding["title"],
            "category": understanding["category"],
            "confidence": understanding["confidence"],
            "skills_found": understanding["skills"],
            "organizations_found": understanding["organizations"],
            "date_extracted": understanding["primary_date"],
            "connections_created": len(relationship_ids),
            "processing_time": total_time,
            "pipeline_stages": stages,  # 👈 Explainable AI — show this in the demo!
        }

    def _fail(self, doc_id: str, filename: str, reason: str) -> Dict[str, Any]:
        logger.warning(f"⚠️ [PIPELINE] Failed for {filename}: {reason}")
        return {
            "success": False,
            "document_id": doc_id,
            "filename": filename,
            "message": reason,
        }

    @staticmethod
    def _ms(start: float) -> float:
        return round((time.time() - start) * 1000, 1)


# Singleton instance
ingestion_pipeline = IngestionPipeline()