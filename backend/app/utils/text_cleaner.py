import re
from typing import List

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s\-\.,;:!?()@#]', '', text)
    return text.strip()

def extract_sentences(text: str, max_sentences: int = 10) -> List[str]:
    """Extract sentences from text"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()][:max_sentences]

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."