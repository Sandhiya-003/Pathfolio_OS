"""Structural document parsing.

Splits resumes, project reports, and similar multi-section documents into
named sections (Education, Experience, Skills, Projects, ...) using heuristic
header detection. This is separate from ClassificationService (which decides
*what kind* of document this is) and from the extractors (which pull out
entities/skills/dates) -- this service is only concerned with *layout*.
"""

import re
from typing import Dict, List

# Canonical section name -> header aliases we should recognize (case-insensitive)
SECTION_ALIASES = {
    "summary": ["summary", "profile", "objective", "about"],
    "education": ["education", "academic background", "academics", "qualifications"],
    "experience": ["experience", "work experience", "employment", "internships", "internship"],
    "projects": ["projects", "project experience", "academic projects"],
    "skills": ["skills", "technical skills", "core competencies", "tools & technologies"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
    "contact": ["contact", "contact information"],
}

_ALL_ALIASES = [
    (canonical, alias)
    for canonical, aliases in SECTION_ALIASES.items()
    for alias in aliases
]
# Longest alias first, so "work experience" matches before "experience"
_ALL_ALIASES.sort(key=lambda pair: len(pair[1]), reverse=True)


def _looks_like_header(line: str) -> bool:
    """A short, mostly-uppercase or title-cased standalone line is likely a header."""
    stripped = line.strip().strip(":").strip()
    if not (2 <= len(stripped) <= 40):
        return False
    if stripped.isupper():
        return True
    # Title Case with no trailing punctuation and few words
    words = stripped.split()
    if 1 <= len(words) <= 4 and stripped[0:1].isupper():
        return True
    return False


class DocumentParser:
    """Parses raw document text into named sections."""

    def identify_section(self, line: str) -> str:
        """Return the canonical section name a header line matches, or '' if none."""
        stripped = line.strip().strip(":").strip().lower()
        if not stripped:
            return ""
        for canonical, alias in _ALL_ALIASES:
            if stripped == alias or stripped.startswith(alias + " ") or stripped == alias + "s":
                return canonical
        return ""

    def parse_sections(self, text: str) -> Dict[str, str]:
        """
        Split `text` into named sections based on detected headers.

        Returns a dict like {"education": "...", "skills": "...", "_preamble": "..."}
        where "_preamble" holds any content before the first recognized header.
        Documents with no recognizable structure return {"_preamble": text}.
        """
        if not text:
            return {}

        lines = text.split("\n")
        sections: Dict[str, List[str]] = {"_preamble": []}
        current = "_preamble"

        for line in lines:
            if _looks_like_header(line):
                match = self.identify_section(line)
                if match:
                    current = match
                    sections.setdefault(current, [])
                    continue
            sections.setdefault(current, []).append(line)

        return {
            name: "\n".join(content_lines).strip()
            for name, content_lines in sections.items()
            if "\n".join(content_lines).strip()
        }

    def has_structure(self, text: str) -> bool:
        """True if at least one recognizable section header was found."""
        sections = self.parse_sections(text)
        return any(name != "_preamble" for name in sections)


# Singleton instance
document_parser = DocumentParser()

# Backwards/forwards-friendly alias -- this module is also commonly reached for
# by the name "parser_service" for resume-shaped documents specifically.
parser_service = document_parser
