import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
from app.core.config import settings
from app.core.logger import logger

class EmbeddingService:
    """Service for generating document embeddings using Sentence-BERT"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not self.model:
            self._load_model()
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )
        return embeddings
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.encode([text], normalize)[0]
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)
        
        # Cosine similarity (embeddings are normalized)
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def semantic_search(self, query: str, corpus: List[str], top_k: int = 5) -> List[dict]:
        """Find most similar texts to a query"""
        query_embedding = self.encode_single(query)
        corpus_embeddings = self.encode(corpus)
        
        # Compute similarities
        similarities = np.dot(corpus_embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "index": int(idx),
                "text": corpus[idx],
                "similarity_score": float(similarities[idx])
            })
        
        return results
    
    def batch_encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings in batches for large datasets"""
        if not self.model:
            self._load_model()
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
