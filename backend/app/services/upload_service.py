"""Upload orchestration service.

Owns the end-to-end pipeline for turning an uploaded file into a stored,
classified, embedded, and relationship-linked document. Kept out of the route
layer (app/api/routes/upload.py) so the same pipeline can be reused by both
the single-file and batch endpoints without going through FastAPI's request
handling twice.
"""

import os
import uuid
import time
from typing import Optional

from fastapi import UploadFile, HTTPException

from app.services.extraction_service import extraction_service
from app.services.classification_service import classification_service
from app.services.vector_service import vector_service
from app.services.relationship_service import relationship_service
from app.db.sqlite_db import sqlite_db
from app.core.config import settings
from app.core.logger import logger
from app.utils.hash_generator import generate_text_hash

ALLOWED_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg']


class UploadService:
    """Handles validation, extraction, classification, storage, and indexing for one upload."""

    def __init__(self):
        self.extraction = extraction_service
        self.classification = classification_service
        self.vector = vector_service
        self.relationships = relationship_service
        self.db = sqlite_db

    def _validate_extension(self, filename: str) -> str:
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(ALLOWED_TYPES)}"
            )
        return file_ext

    def _validate_size(self, content: bytes) -> None:
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File is too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

    def _find_duplicate(self, user_id: str, extracted_text: str) -> Optional[dict]:
        """
        Check whether this user already has a document with identical extracted
        text. No schema migration needed -- hashes are computed on the fly
        against each existing document's stored text.
        """
        if not extracted_text.strip():
            return None

        incoming_hash = generate_text_hash(extracted_text)
        for doc in self.db.get_all_documents(user_id):
            existing_text = doc.get("extracted_text") or ""
            if existing_text and generate_text_hash(existing_text) == incoming_hash:
                return doc
        return None

    async def process(self, file: UploadFile, user_id: str) -> dict:
        """Run the full ingestion pipeline for a single uploaded file."""
        start_time = time.time()
        file_ext = self._validate_extension(file.filename)

        try:
            doc_id = str(uuid.uuid4())
            file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}{file_ext}")

            content = await file.read()
            self._validate_size(content)

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"📁 Uploaded file: {file.filename}")

            extraction_result = self.extraction.extract(file_path)
            extracted_text = extraction_result.get('text', '')

            if not extracted_text.strip():
                return {
                    "success": False,
                    "message": "Could not extract text from document. It might be empty or scanned.",
                    "document_id": doc_id
                }

            duplicate = self._find_duplicate(user_id, extracted_text)
            if duplicate:
                # Clean up the redundant file we just wrote before returning
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    "success": False,
                    "message": f"This looks identical to an existing document: \"{duplicate['title']}\".",
                    "document_id": duplicate["id"],
                    "duplicate_of": duplicate["id"],
                }

            doc_data = self.classification.process_document(extracted_text, file.filename)
            description = doc_data.get("summary") or doc_data.get("reasoning", "")

            document = {
                "id": doc_id,
                "user_id": user_id,
                "title": doc_data['title'],
                "category": doc_data['category'],
                "file_type": file_ext[1:],
                "file_path": file_path,
                "original_filename": file.filename,
                "extracted_text": extracted_text,
                "skills": doc_data['skills'],
                "organizations": doc_data['organizations'],
                "date_extracted": doc_data['primary_date'],
                "description": description,
                "embedding_id": doc_id
            }

            self.db.insert_document(document)

            self.vector.add_document(
                doc_id=doc_id,
                text=extracted_text,
                metadata={
                    "title": document['title'],
                    "category": document['category'],
                    "skills": ",".join(document['skills']),
                    "user_id": user_id
                }
            )

            self.relationships.build_relationships(doc_id, doc_data)

            processing_time = time.time() - start_time

            return {
                "success": True,
                "message": "Document processed successfully!",
                "document_id": doc_id,
                "filename": file.filename,
                "category": doc_data['category'],
                "skills_found": doc_data['skills'],
                "organizations_found": doc_data['organizations'],
                "date_extracted": doc_data['primary_date'],
                "processing_time": round(processing_time, 2)
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Singleton instance
upload_service = UploadService()