from typing import List, Dict, Optional
from app.db.chroma_db import chroma_client
from app.services.embedding_service import embedding_service
from app.core.logger import logger

class VectorService:
    """Service for managing vector embeddings and semantic search"""
    
    def __init__(self):
        self.chroma = chroma_client
        self.embedding = embedding_service
    
    def add_document(self, doc_id: str, text: str, metadata: Dict) -> bool:
        """Add a document to the vector database"""
        try:
            # Generate embedding
            embedding = self.embedding.encode_single(text)
            
            # Add to ChromaDB
            return self.chroma.add_document(
                doc_id=doc_id,
                text=text,
                metadata={
                    **metadata,
                    "text_preview": text[:500]  # Store preview for display
                }
            )
        except Exception as e:
            logger.error(f"❌ Failed to add document to vector DB: {e}")
            return False
    
    def search(self, query: str, filters: Dict = None, limit: int = 10) -> List[Dict]:
        """
        Semantic search across all documents
        
        Args:
            query: Natural language search query
            filters: Optional metadata filters
            limit: Maximum results
        
        Returns:
            List of matching documents with similarity scores
        """
        try:
            results = self.chroma.search(
                query=query,
                n_results=limit,
                filters=filters
            )
            
            return results.get('results', [])
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector database"""
        return self.chroma.delete(doc_id)
    
    def get_similar_documents(self, doc_id: str, limit: int = 5) -> List[Dict]:
        """Find documents similar to a given document"""
        # Get the document's text
        doc = self.chroma.get_by_id(doc_id)
        if not doc:
            return []
        
        # Search for similar content
        results = self.search(doc['document'], limit=limit + 1)
        
        # Filter out the original document
        return [r for r in results if r['id'] != doc_id][:limit]
    
    def rebuild_index(self, documents: List[Dict]) -> int:
        """
        Rebuild the entire vector index
        
        Args:
            documents: List of {"id", "text", "metadata"} dicts
        
        Returns:
            Number of documents indexed
        """
        count = 0
        for doc in documents:
            try:
                self.add_document(
                    doc_id=doc['id'],
                    text=doc['text'],
                    metadata=doc.get('metadata', {})
                )
                count += 1
            except Exception as e:
                logger.error(f"❌ Failed to index document {doc.get('id')}: {e}")
        
        return count

# Singleton instance
vector_service = VectorService()
