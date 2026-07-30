from typing import List, Dict, Optional
import time
from app.services.vector_service import vector_service
from app.db.sqlite_db import sqlite_db
from app.core.logger import logger

class RetrievalService:
    """Service for intelligent document retrieval"""
    
    def __init__(self):
        self.vector = vector_service
        self.db = sqlite_db
    
    def search(self, query: str, filters: Dict = None, limit: int = 10) -> Dict:
        """
        Perform semantic search with natural language query
        
        Args:
            query: Natural language search query
            filters: Optional category/date filters
            limit: Maximum results
        
        Returns:
            Formatted search results with context
        """
        start_time = time.time()
        
        # Perform vector search
        search_results = self.vector.search(
            query=query,
            filters=filters,
            limit=limit
        )
        
        # Enrich results with document metadata
        enriched_results = []
        for result in search_results:
            doc = self.db.get_document(result['id'])
            if doc:
                enriched_results.append({
                    "document_id": doc['id'],
                    "title": doc['title'],
                    "category": doc['category'],
                    "snippet": self._generate_snippet(doc['extracted_text'], query),
                    "similarity_score": result['similarity_score'],
                    "skills": doc.get('skills', []),
                    "date": doc.get('date_extracted'),
                    "highlights": self._generate_highlights(doc['extracted_text'], query)
                })
        
        # Generate suggestions
        suggestions = self._generate_suggestions(query, enriched_results)
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "query": query,
            "total_results": len(enriched_results),
            "results": enriched_results,
            "suggestions": suggestions,
            "processing_time_ms": round(processing_time, 2)
        }
    
    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Generate a relevant snippet from the text"""
        if not text:
            return ""
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Find query terms in text
        query_terms = query_lower.split()
        for term in query_terms:
            idx = text_lower.find(term)
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(text), idx + 150)
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                return snippet
        
        # Fallback to beginning
        return text[:max_length] + ("..." if len(text) > max_length else "")
    
    def _generate_highlights(self, text: str, query: str) -> List[str]:
        """Generate highlighted segments matching the query"""
        highlights = []
        text_lower = text.lower()
        query_terms = query.lower().split()
        
        for term in query_terms:
            if len(term) < 3:
                continue
            
            # Find all occurrences
            start = 0
            while True:
                idx = text_lower.find(term, start)
                if idx == -1:
                    break
                
                # Extract surrounding context
                context_start = max(0, idx - 30)
                context_end = min(len(text), idx + len(term) + 30)
                highlight = text[context_start:context_end]
                
                if context_start > 0:
                    highlight = "..." + highlight
                if context_end < len(text):
                    highlight = highlight + "..."
                
                highlights.append(highlight.strip())
                start = idx + 1
                
                if len(highlights) >= 5:  # Limit highlights
                    break
        
        return list(set(highlights))[:5]
    
    def _generate_suggestions(self, query: str, results: List[Dict]) -> List[str]:
        """Generate follow-up query suggestions"""
        suggestions = []
        
        # Extract categories from results
        categories = set(r['category'] for r in results)
        
        # Suggest related searches
        if 'project' in query.lower():
            suggestions.append("Show certifications related to these projects")
            suggestions.append("Find similar internship experiences")
        
        if 'certification' in query.lower() or 'certificate' in query.lower():
            suggestions.append("View all skills from these certifications")
            suggestions.append("Find projects using these technologies")
        
        if not suggestions:
            suggestions = [
                "Show documents by category",
                "View timeline of achievements",
                "See skill development over time"
            ]
        
        return suggestions[:3]
    
    def get_documents_by_skill(self, skill: str, user_id: str) -> List[Dict]:
        """Get all documents related to a specific skill, scoped to a user"""
        # Search for the skill within this user's documents only
        results = self.search(f"documents about {skill}", filters={"user_id": user_id}, limit=20)

        # Filter to documents that actually mention the skill
        filtered = [
            r for r in results['results']
            if skill.lower() in [s.lower() for s in r.get('skills', [])]
        ]

        return filtered

    def get_recent_documents(self, user_id: str, limit: int = 10, category: str = None) -> List[Dict]:
        """Get most recent documents for a user"""
        docs = self.db.get_all_documents(user_id)

        if category:
            docs = [d for d in docs if d['category'] == category]

        return docs[:limit]

# Singleton instance
retrieval_service = RetrievalService()
