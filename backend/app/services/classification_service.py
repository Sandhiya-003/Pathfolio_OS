import os
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.constants import DOCUMENT_CATEGORIES
from app.core.logger import logger
from app.ai.extractors.entity_extractor import entity_extractor
from app.ai.extractors.skill_extractor import skill_extractor
from app.ai.extractors.date_extractor import date_extractor
from app.services.summarization_service import summarization_service

try:
    import spacy  # type: ignore[import]
except ImportError:
    spacy = None  # type: ignore[assignment]


class ClassificationService:
    """Service for classifying documents and orchestrating extraction (entities, skills, dates)."""

    def __init__(self):
        self.nlp = None
        self.entities = entity_extractor
        self.skills = skill_extractor
        self.dates = date_extractor
        self._load_model()

    def _load_model(self):
        """Load spaCy model for NER and hand it to the entity extractor"""
        try:
            import spacy
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
            self.entities.set_model(self.nlp)
            logger.info("✅ spaCy model loaded")
        except ModuleNotFoundError:
            logger.error("spaCy package not installed. Entity extraction disabled.")
            self.nlp = None
        except OSError:
            logger.warning("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            self.entities.set_model(self.nlp)
            logger.info("✅ spaCy model downloaded and loaded")

    def classify(self, text: str, filename: str = "") -> Dict:
        """
        Classify a document into a category

        Args:
            text: Extracted text from the document
            filename: Original filename for additional context

        Returns:
            {
                "category": str,
                "confidence": float,
                "reasoning": str
            }
        """
        # Combine text and filename for classification
        combined_text = f"{filename} {text[:1000]}"
        combined_lower = combined_text.lower()

        # Score each category
        scores = {}

        for category, info in DOCUMENT_CATEGORIES.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in combined_lower:
                    score += 1

            # Boost score based on filename matches
            if any(kw in filename.lower() for kw in info["keywords"]):
                score += 3

            scores[category] = score

        # Get best category
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # Calculate confidence (normalize to 0-1)
        confidence = min(1.0, max_score / 3.0) if max_score > 0 else 0.3

        # Fallback for low confidence
        if max_score == 0:
            best_category = "other"
            confidence = 0.5

        logger.info(f"📁 Classified as: {best_category} (confidence: {confidence:.2f})")

        return {
            "category": best_category,
            "confidence": confidence,
            "reasoning": f"Matched keywords: {[k for k in DOCUMENT_CATEGORIES[best_category]['keywords'] if k in combined_lower]}"
        }

    def extract_entities(self, text: str) -> Dict:
        """Extract named entities from text (delegates to EntityExtractor)"""
        return self.entities.extract(text)

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text (delegates to SkillExtractor)"""
        return self.skills.extract(text)

    def extract_date(self, text: str) -> Optional[str]:
        """Extract a representative date from text (delegates to DateExtractor)"""
        return self.dates.extract(text)

    def extract_title(self, text: str, filename: str) -> str:
        """
        Generate or extract title from document

        Args:
            text: Document text
            filename: Original filename

        Returns:
            Title string
        """
        # Clean up filename for title
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")

        # Try to extract from first line if it looks like a title
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            if 5 < len(first_line) < 100 and first_line.isupper():
                title = first_line

        return title[:200]  # Limit title length

    def process_document(self, text: str, filename: str) -> Dict:
        """
        Full document processing pipeline

        Returns comprehensive extracted information
        """
        classification = self.classify(text, filename)
        entities = self.extract_entities(text)
        skills = self.extract_skills(text)
        date = self.extract_date(text)
        title = self.extract_title(text, filename)
        summary = summarization_service.summarize(text)

        return {
            "title": title,
            "category": classification["category"],
            "confidence": classification["confidence"],
            "reasoning": classification["reasoning"],
            "summary": summary,
            "skills": skills,
            "organizations": entities["organizations"],
            "dates": entities["dates"],
            "locations": entities["locations"],
            "primary_date": date,
            "entities": entities
        }


# Singleton instance
classification_service = ClassificationService()
