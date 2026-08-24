import chromadb
from chromadb.config import Settings
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.core.logger import logger

class ChromaDBClient:
    """ChromaDB client for vector embeddings and semantic search"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # PersistentClient actually writes to disk and reloads on restart.
            # The old chromadb.Client(Settings(persist_directory=...)) pattern
            # silently falls back to an in-memory-only store in chromadb 0.4.x
            # unless chroma_db_impl="duckdb+parquet" is also set -- which is why
            # every server restart was wiping the vector index even though the
            # SQLite database (documents, skills) persisted fine.
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_DIR,
                settings=Settings(anonymized_telemetry=False),
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection("portfolio_documents")
                logger.info(f"✅ Loaded existing ChromaDB collection ({self.collection.count()} documents)")
            except Exception:
                self.collection = self.client.create_collection(
                    name="portfolio_documents",
                    metadata={
                        "description": "PortfolioOS document embeddings",
                        "hnsw:space": "cosine"
                    }
                )
                logger.info("✅ Created new ChromaDB collection")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            raise
    
    def add_document(
        self, doc_id: str, text: str, metadata: Dict[str, Any], embedding: List[float]
    ) -> bool:
        """Add a document embedding to ChromaDB"""
        try:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata],
                embeddings=[embedding],
            )
            logger.info(f"✅ Added document {doc_id} to vector DB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add document to ChromaDB: {e}")
            return False
    
    def search(
        self, query: str, query_embedding: List[float], n_results: int = 10, filters: Dict = None
    ) -> Dict:
        """
        Semantic search using vector similarity
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"category": "project"})
        
        Returns:
            Search results with document IDs and similarity scores
        """
        try:
            where_clause = None
            if filters:
                where_clause = filters
            
            indexed_count = self.collection.count()
            if not indexed_count:
                return {"success": True, "results": [], "total": 0}

            # Chroma rejects a requested result count larger than the index.
            # This is common for a new portfolio, where VectorService requests
            # a wider candidate pool before applying its relevance threshold.
            n_results = min(n_results, indexed_count)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "document": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 1.0,
                        "similarity_score": 1 - results['distances'][0][i] if results['distances'] else 0
                    })
            
            return {
                "success": True,
                "results": formatted_results,
                "total": len(formatted_results)
            }
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return {"success": False, "results": [], "error": str(e)}
    
    def get_by_id(self, doc_id: str) -> Optional[Dict]:
        """Get a document by ID"""
        try:
            result = self.collection.get(ids=[doc_id], include=["documents", "metadatas"])
            if result['ids']:
                return {
                    "id": result['ids'][0],
                    "document": result['documents'][0] if result['documents'] else "",
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get document: {e}")
            return None
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document from the vector database"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"✅ Deleted document {doc_id} from vector DB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete document: {e}")
            return False
    
    def count(self) -> int:
        """Get total number of documents in the collection"""
        return self.collection.count()
    
    def get_all(self, limit: int = 100) -> List[Dict]:
        """Get all documents (for debugging/rebuilding)"""
        try:
            result = self.collection.get(limit=limit, include=["documents", "metadatas"])
            return [
                {
                    "id": result['ids'][i],
                    "document": result['documents'][i] if result['documents'] else "",
                    "metadata": result['metadatas'][i] if result['metadatas'] else {}
                }
                for i in range(len(result['ids']))
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get all documents: {e}")
            return []

# Singleton instance
chroma_client = ChromaDBClient()
