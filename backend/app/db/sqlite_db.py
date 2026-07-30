import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.core.logger import logger

class SQLiteDB:
    """SQLite database for document metadata storage"""
    
    def __init__(self):
        self.db_path = os.path.join(settings.BASE_DIR, "portfolioos.db")
        self.connection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Create tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                extracted_text TEXT,
                skills TEXT,  -- JSON array
                organizations TEXT,  -- JSON array
                date_extracted TEXT,
                description TEXT,
                embedding_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES documents(id)
            )
        """)
        
        # Skills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                document_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)")
        
        conn.commit()
        logger.info("✅ SQLite database initialized")
    
    def _get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    # ---- Users ----

    def create_user(self, user: Dict[str, Any]) -> str:
        """Insert a new user. Raises sqlite3.IntegrityError if username/email taken."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                user["username"],
                user["email"],
                user["password_hash"],
                user.get("full_name"),
            ),
        )
        conn.commit()
        return user["id"]

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def insert_document(self, doc: Dict[str, Any]) -> str:
        """Insert a new document"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documents (
                id, user_id, title, category, file_type, file_path,
                original_filename, extracted_text, skills, organizations,
                date_extracted, description, embedding_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.get('id'),
            doc.get('user_id', 'default_user'),
            doc.get('title'),
            doc.get('category'),
            doc.get('file_type'),
            doc.get('file_path'),
            doc.get('original_filename'),
            doc.get('extracted_text'),
            json.dumps(doc.get('skills', [])),
            json.dumps(doc.get('organizations', [])),
            doc.get('date_extracted'),
            doc.get('description'),
            doc.get('embedding_id')
        ))
        
        conn.commit()
        return doc.get('id')
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        
        if row:
            doc = dict(row)
            doc['skills'] = json.loads(doc.get('skills', '[]'))
            doc['organizations'] = json.loads(doc.get('organizations', '[]'))
            return doc
        return None
    
    def get_all_documents(self, user_id: str = "default_user") -> List[Dict]:
        """Get all documents for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            doc = dict(row)
            doc['skills'] = json.loads(doc.get('skills', '[]'))
            doc['organizations'] = json.loads(doc.get('organizations', '[]'))
            documents.append(doc)
        
        return documents
    
    def get_documents_by_category(self, category: str, user_id: str = "default_user") -> List[Dict]:
        """Get documents by category"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM documents WHERE user_id = ? AND category = ? ORDER BY created_at DESC",
            (user_id, category)
        )
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            doc = dict(row)
            doc['skills'] = json.loads(doc.get('skills', '[]'))
            doc['organizations'] = json.loads(doc.get('organizations', '[]'))
            documents.append(doc)
        
        return documents
    
    def update_document(self, doc_id: str, updates: Dict) -> bool:
        """Update a document"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for key, value in updates.items():
            if isinstance(value, list):
                value = json.dumps(value)
            cursor.execute(
                f"UPDATE documents SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (value, doc_id)
            )
        
        conn.commit()
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        cursor.execute("DELETE FROM relationships WHERE source_id = ? OR target_id = ?", (doc_id, doc_id))
        conn.commit()
        
        return True
    
    def insert_relationship(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0) -> str:
        """Insert a relationship"""
        import uuid
        rel_id = str(uuid.uuid4())
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO relationships (id, source_id, target_id, relationship_type, weight)
            VALUES (?, ?, ?, ?, ?)
        """, (rel_id, source_id, target_id, rel_type, weight))
        
        conn.commit()
        return rel_id
    
    def get_relationships(self, doc_id: str) -> List[Dict]:
        """Get all relationships for a document"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM relationships 
            WHERE source_id = ? OR target_id = ?
        """, (doc_id, doc_id))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def upsert_skill(self, skill_name: str, category: str = None) -> str:
        """Insert or update a skill"""
        import uuid
        skill_id = skill_name.lower().replace(" ", "_")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO skills (id, name, category)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                document_count = document_count + 1
        """, (skill_id, skill_name.lower(), category))
        
        conn.commit()
        return skill_id
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills with counts"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM skills ORDER BY document_count DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self, user_id: str = "default_user") -> Dict:
        """Get document statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total documents
        cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_id,))
        total_docs = cursor.fetchone()['count']
        
        # Documents by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM documents WHERE user_id = ?
            GROUP BY category
        """, (user_id,))
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # Skills count
        cursor.execute("SELECT COUNT(*) as count FROM skills")
        skills_count = cursor.fetchone()['count']
        
        return {
            "total_documents": total_docs,
            "by_category": by_category,
            "skills_count": skills_count
        }
    
    def close(self):
        if self.connection:
            self.connection.close()

    def delete_relationships_for_document(self, doc_id: str) -> int:
        """Remove every relationship row that references this document, as
            either source or target. Called whenever a document is deleted so
          the knowledge graph doesn't accumulate edges pointing at nothing."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
        "DELETE FROM relationships WHERE source_id = ? OR target_id = ?",
        (doc_id, doc_id),
    )
        conn.commit()
        return cursor.rowcount        

# Singleton instance
sqlite_db = SQLiteDB()
