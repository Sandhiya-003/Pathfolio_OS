from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
from app.db.sqlite_db import sqlite_db
from app.core.config import settings
from app.core.constants import DOCUMENT_CATEGORIES
from app.core.logger import logger

class TimelineService:
    """Service for generating user journey timelines"""
    
    def __init__(self):
        self.db = sqlite_db
    
    def generate_timeline(self, user_id: str = "default_user") -> Dict:
        """
        Generate a complete timeline of user's documents
        
        Returns:
            Timeline organized by year
        """
        documents = self.db.get_all_documents(user_id)
        
        if not documents:
            return {
                "user_id": user_id,
                "total_years": 0,
                "total_events": 0,
                "timeline": [],
                "generated_at": datetime.now().isoformat()
            }
        
        # Group documents by year
        by_year = defaultdict(list)
        
        for doc in documents:
            date_str = doc.get('date_extracted') or doc.get('created_at', '')
            
            # Extract year
            try:
                if 'T' in date_str:
                    year = int(date_str.split('T')[0].split('-')[0])
                else:
                    # Try to extract from various formats
                    import re
                    year_match = re.search(r'\b(20\d{2})\b', date_str)
                    year = int(year_match.group(1)) if year_match else datetime.now().year
            except:
                year = datetime.now().year
            
            by_year[year].append({
                   "id": doc['id'],
                   "title": doc['title'],
                   "category": doc['category'],
                   "description": doc.get('description', ''),
                   "date": doc.get('date_extracted') or '',
                   "skills": doc.get('skills', []),
                   "document_id": doc['id'],
                   "emoji": DOCUMENT_CATEGORIES.get(doc['category'], {}).get('emoji', '📄')
})
        
        # Build timeline
        timeline = []
        years = sorted(by_year.keys(), reverse=True)
        
        for year in years:
            events = sorted(by_year[year], key=lambda x: x.get('date') or '', reverse=True)
            
            # Generate year summary
            categories_in_year = set(e['category'] for e in events)
            summary = self._generate_year_summary(year, events)
            
            timeline.append({
                "year": year,
                "events": events,
                "summary": summary,
                "event_count": len(events),
                "categories": list(categories_in_year)
            })
        
        total_events = sum(len(year_data['events']) for year_data in timeline)
        
        return {
            "user_id": user_id,
            "total_years": len(timeline),
            "total_events": total_events,
            "timeline": timeline,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_year_summary(self, year: int, events: List[Dict]) -> str:
        """Generate a human-readable summary for a year's events"""
        categories = {}
        for event in events:
            cat = event['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        parts = []
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            emoji = DOCUMENT_CATEGORIES.get(cat, {}).get('emoji', '📄')
            parts.append(f"{emoji} {count} {cat}(s)")
        
        return f"{year}: " + " • ".join(parts)
    
    def get_timeline_stats(self, user_id: str = "default_user") -> Dict:
        """Get statistics about the user's timeline"""
        stats = self.db.get_stats(user_id)
        skills = self.db.get_all_skills()
        
        # Top skills
        top_skills = [
            {"name": s['name'], "count": s['document_count']}
            for s in sorted(skills, key=lambda x: -x['document_count'])[:10]
        ]
        
        # Career growth summary
        timeline_data = self.generate_timeline(user_id)
        career_growth = self._generate_career_summary(timeline_data)
        
        return {
            "total_documents": stats['total_documents'],
            "documents_by_category": stats['by_category'],
            "skills_count": stats['skills_count'],
            "top_skills": top_skills,
            "career_growth_summary": career_growth
        }
    
    def _generate_career_summary(self, timeline: Dict) -> str:
        """Generate a career growth summary"""
        if not timeline.get('timeline'):
            return "Start your journey by uploading your first document!"
        
        years = [year['year'] for year in timeline['timeline']]
        if len(years) > 1:
            span = max(years) - min(years)
            return f"Over {span} year(s), you've built a diverse portfolio with {timeline['total_events']} documented achievements."
        else:
            return f"In {years[0]}, you've documented {timeline['total_events']} achievements. Keep building!"

# Singleton instance
timeline_service = TimelineService()
