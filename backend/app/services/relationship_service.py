from typing import List, Dict, Optional
from app.db.sqlite_db import sqlite_db
from app.services.vector_service import vector_service
from app.core.config import settings
from app.core.logger import logger

class RelationshipService:
    """Service for building and querying document relationships"""
    
    def __init__(self):
        self.db = sqlite_db
        self.vector = vector_service
    
    def build_relationships(self, doc_id: str, doc_data: Dict) -> List[str]:
        """
        Build relationships for a new document
        
        Args:
            doc_id: Document ID
            doc_data: Extracted document data
        
        Returns:
            List of created relationship IDs
        """
        created_rels = []
        
        # 1. Create skill relationships
        skills = doc_data.get('skills', [])
        for skill in skills:
            skill_id = self.db.upsert_skill(skill, doc_data.get('category'))
            rel_id = self.db.insert_relationship(
                source_id=doc_id,
                target_id=f"skill_{skill_id}",
                rel_type="document_to_skill",
                weight=1.0
            )
            created_rels.append(rel_id)
        
        # 2. Find similar documents using vector similarity
        similar_docs = self.vector.get_similar_documents(doc_id, limit=5)
        for similar in similar_docs:
            if similar['similarity_score'] >= settings.SIMILARITY_THRESHOLD:
                rel_id = self.db.insert_relationship(
                    source_id=doc_id,
                    target_id=similar['id'],
                    rel_type="similar_document",
                    weight=similar['similarity_score']
                )
                created_rels.append(rel_id)
        
        # 3. Create category-based relationships
        category = doc_data.get('category')
        if category:
            existing_docs = self.db.get_documents_by_category(category)
            for existing in existing_docs[:10]:  # Limit to recent 10
                if existing['id'] != doc_id:
                    # Check for skill overlap
                    existing_skills = set(existing.get('skills', []))
                    new_skills = set(skills)
                    overlap = len(existing_skills & new_skills)
                    
                    if overlap > 0:
                        rel_id = self.db.insert_relationship(
                            source_id=doc_id,
                            target_id=existing['id'],
                            rel_type="same_category_skill_overlap",
                            weight=overlap / max(len(existing_skills | new_skills), 1)
                        )
                        created_rels.append(rel_id)
        
        logger.info(f"🔗 Built {len(created_rels)} relationships for document {doc_id}")
        return created_rels
    
    def get_relationships(self, doc_id: str) -> Dict:
        """Get all relationships for a document"""
        relationships = self.db.get_relationships(doc_id)
        
        # Group by type
        grouped = {
            "skills": [],
            "similar_documents": [],
            "category_peers": []
        }
        
        for rel in relationships:
            if rel['relationship_type'] == 'document_to_skill':
                grouped['skills'].append(rel)
            elif rel['relationship_type'] == 'similar_document':
                grouped['similar_documents'].append(rel)
            else:
                grouped['category_peers'].append(rel)
        
        return grouped
    
    def get_skill_graph(self, user_id: str) -> Dict:
        """Get the complete skill relationship graph for a specific user"""
        # Get this user's documents only
        documents = self.db.get_all_documents(user_id)
        
        # Build nodes
        nodes = []
        skill_set = set()
        
        for doc in documents:
            nodes.append({
                "id": doc['id'],
                "label": doc['title'],
                "type": "document",
                "category": doc['category']
            })
            
            for skill in doc.get('skills', []):
                skill_id = f"skill_{skill.lower().replace(' ', '_')}"
                if skill_id not in skill_set:
                    skill_set.add(skill_id)
                    nodes.append({
                        "id": skill_id,
                        "label": skill,
                        "type": "skill",
                        "size": 1
                    })
        
        # Build edges (aggregate relationships across every document, deduped)
        edges = []
        seen_edges = set()
        for doc in documents:
            relationships = self.db.get_relationships(doc['id'])
            for rel in relationships:
                edge_key = (rel['source_id'], rel['target_id'], rel['relationship_type'])
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append({
                    "source": rel['source_id'],
                    "target": rel['target_id'],
                    "type": rel['relationship_type'],
                    "weight": rel['weight']
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_related_documents(self, doc_id: str, limit: int = 5) -> List[Dict]:
        """Get documents related to a given document"""
        relationships = self.get_relationships(doc_id)
        
        related_ids = set()
        
        # Add similar documents
        for rel in relationships.get('similar_documents', []):
            target = rel['target_id'] if rel['source_id'] == doc_id else rel['source_id']
            related_ids.add(target)
        
        # Add category peers
        for rel in relationships.get('category_peers', []):
            target = rel['target_id'] if rel['source_id'] == doc_id else rel['source_id']
            related_ids.add(target)
        
        # Fetch full documents
        related_docs = []
        for rel_id in list(related_ids)[:limit]:
            if not rel_id.startswith("skill_"):
                doc = self.db.get_document(rel_id)
                if doc:
                    related_docs.append(doc)
        
        return related_docs

# Singleton instance
relationship_service = RelationshipService()
