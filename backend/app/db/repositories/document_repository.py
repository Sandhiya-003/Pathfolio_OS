"""Document-focused data access.

A narrower, purpose-built interface over SQLiteDB for code that only needs
document CRUD and shouldn't have to import (or know about) the full database
client -- relationships, skills, and user tables included. Wraps the shared
`sqlite_db` singleton rather than opening a second connection to the same
database file.
"""

from typing import Dict, List, Optional

from app.db.sqlite_db import sqlite_db


class DocumentRepository:
    """Read/write access to the `documents` table."""

    def __init__(self, db=None):
        self.db = db or sqlite_db

    def create(self, document: Dict) -> str:
        return self.db.insert_document(document)

    def get_by_id(self, doc_id: str) -> Optional[Dict]:
        return self.db.get_document(doc_id)

    def get_owned(self, doc_id: str, user_id: str) -> Optional[Dict]:
        """Get a document only if it belongs to `user_id`; otherwise None."""
        doc = self.db.get_document(doc_id)
        if doc and doc.get("user_id") == user_id:
            return doc
        return None

    def list_for_user(self, user_id: str) -> List[Dict]:
        return self.db.get_all_documents(user_id)

    def list_by_category(self, category: str, user_id: str) -> List[Dict]:
        return self.db.get_documents_by_category(category, user_id)

    def update(self, doc_id: str, updates: Dict) -> bool:
        return self.db.update_document(doc_id, updates)

    def delete(self, doc_id: str) -> bool:
        return self.db.delete_document(doc_id)

    def stats_for_user(self, user_id: str) -> Dict:
        return self.db.get_stats(user_id)


# Singleton instance
document_repository = DocumentRepository()
