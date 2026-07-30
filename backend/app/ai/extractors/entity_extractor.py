"""Extracts named entities (organizations, dates, locations, people) via spaCy NER.

Kept separate from ClassificationService so the spaCy model can be shared/injected
rather than re-loaded per extractor, and so entity extraction can be tested or
swapped independently of category classification logic.
"""

from typing import Dict, List, Optional

from app.core.logger import logger

ENTITY_KEYS = ("organizations", "dates", "locations", "persons")

_LABEL_MAP = {
    "ORG": "organizations",
    "DATE": "dates",
    "TIME": "dates",
    "GPE": "locations",
    "PERSON": "persons",
}


class EntityExtractor:
    """Extracts named entities from text using a spaCy NLP pipeline."""

    def __init__(self, nlp=None, max_chars: int = 50000, max_per_type: int = 10):
        """
        Args:
            nlp: A loaded spaCy Language object. If None, extraction is a no-op
                 until one is provided via `set_model`.
            max_chars: Text is truncated to this length before running NER
                       (spaCy pipelines get slow/expensive on very long documents).
            max_per_type: Max number of deduplicated entities returned per category.
        """
        self.nlp = nlp
        self.max_chars = max_chars
        self.max_per_type = max_per_type

    def set_model(self, nlp) -> None:
        """Attach (or replace) the spaCy model used for extraction."""
        self.nlp = nlp

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract organizations, dates, locations, and people from text.

        Returns:
            {"organizations": [...], "dates": [...], "locations": [...], "persons": [...]}
        """
        empty = {key: [] for key in ENTITY_KEYS}

        if not text:
            return empty

        if not self.nlp:
            logger.warning("spaCy model unavailable; skipping entity extraction.")
            return empty

        try:
            doc = self.nlp(text[: self.max_chars])
            entities = {key: [] for key in ENTITY_KEYS}

            for ent in doc.ents:
                bucket = _LABEL_MAP.get(ent.label_)
                if bucket:
                    entities[bucket].append(ent.text)

            # Deduplicate while capping size
            for key in entities:
                entities[key] = list(dict.fromkeys(entities[key]))[: self.max_per_type]

            return entities

        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return empty


# Singleton instance (model attached lazily by ClassificationService)
entity_extractor = EntityExtractor()
