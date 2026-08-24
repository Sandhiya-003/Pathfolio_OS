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
    """Service for classifying documents and orchestrating extraction."""

    def __init__(self):
        # spaCy is intentionally NOT loaded during startup.
        # It will be loaded only when entity extraction is actually needed.
        self.nlp = None

        self.entities = entity_extractor
        self.skills = skill_extractor
        self.dates = date_extractor

    def _load_model(self) -> bool:
        """
        Lazily load the spaCy model when entity extraction is required.

        Returns:
            True if the spaCy model is available, otherwise False.
        """

        # Model is already loaded
        if self.nlp is not None:
            return True

        # spaCy package is not installed
        if spacy is None:
            logger.warning(
                "spaCy package not installed. Entity extraction disabled."
            )
            return False

        try:
            logger.info("Loading spaCy model...")

            self.nlp = spacy.load("en_core_web_sm")

            # Give the loaded model to the entity extractor
            self.entities.set_model(self.nlp)

            logger.info("spaCy model loaded successfully")

            return True

        except OSError:
            # Do NOT attempt to download the model during runtime.
            # Production deployments should have dependencies installed
            # during the Docker build.
            logger.warning(
                "spaCy model 'en_core_web_sm' is unavailable. "
                "Entity extraction disabled."
            )

            self.nlp = None

            return False

        except Exception as exc:
            logger.exception(
                f"Failed to load spaCy model: {exc}"
            )

            self.nlp = None

            return False

    def classify(self, text: str, filename: str = "") -> Dict:
        """
        Classify a document into a category.

        Args:
            text: Extracted document text.
            filename: Original filename.

        Returns:
            Dictionary containing category, confidence and reasoning.
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
            if any(
                keyword in filename.lower()
                for keyword in info["keywords"]
            ):
                score += 3

            scores[category] = score

        # Get best category
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # Calculate confidence
        confidence = (
            min(1.0, max_score / 3.0)
            if max_score > 0
            else 0.3
        )

        # Fallback for low confidence
        if max_score == 0:
            best_category = "other"
            confidence = 0.5

        logger.info(
            f"Classified as: {best_category} "
            f"(confidence: {confidence:.2f})"
        )

        return {
            "category": best_category,
            "confidence": confidence,
            "reasoning": (
                f"Matched keywords: "
                f"{[k for k in DOCUMENT_CATEGORIES[best_category]['keywords'] if k in combined_lower]}"
            ),
        }

    def extract_entities(self, text: str) -> Dict:
        """
        Extract named entities from text.

        spaCy is loaded lazily here rather than during application startup.
        """

        # Load spaCy only when entity extraction is actually requested
        if self.nlp is None:
            self._load_model()

        return self.entities.extract(text)

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        return self.skills.extract(text)

    def extract_date(self, text: str) -> Optional[str]:
        """Extract a representative date from text."""
        return self.dates.extract(text)

    def extract_title(self, text: str, filename: str) -> str:
        """
        Generate or extract a title from the document.

        Args:
            text: Document text.
            filename: Original filename.

        Returns:
            Extracted/generated title.
        """

        # Clean up filename for title
        title = (
            os.path.splitext(filename)[0]
            .replace("_", " ")
            .replace("-", " ")
        )

        # Try to extract from first line if it looks like a title
        lines = text.split("\n")

        if lines:
            first_line = lines[0].strip()

            if 5 < len(first_line) < 100 and first_line.isupper():
                title = first_line

        return title[:200]

    def process_document(self, text: str, filename: str) -> Dict:
        """
        Full document processing pipeline.

        Returns:
            Comprehensive extracted document information.
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
            "entities": entities,
        }


# Singleton instance
#
# IMPORTANT:
# Creating this object no longer loads spaCy.
# The spaCy model is loaded only when extract_entities()
# is actually called.
classification_service = ClassificationService()
