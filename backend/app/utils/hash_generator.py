"""Content hashing utilities.

Used to detect duplicate uploads (same file content ingested twice) without
needing exact-filename matches -- useful since students often re-download or
rename the same certificate before uploading it.
"""

import hashlib


def generate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Hash a file's contents by streaming it in chunks (safe for large files)."""
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_bytes_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Hash an in-memory bytes object (e.g. an upload before it's written to disk)."""
    return hashlib.new(algorithm, data).hexdigest()


def generate_text_hash(text: str, algorithm: str = "sha256") -> str:
    """Hash a text string, e.g. a document's extracted text, for near-duplicate checks."""
    return hashlib.new(algorithm, text.encode("utf-8", errors="ignore")).hexdigest()
