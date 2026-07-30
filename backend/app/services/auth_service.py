import uuid
import sqlite3
from typing import Optional, Dict

from app.db.sqlite_db import sqlite_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logger import logger


class AuthError(Exception):
    """Raised for expected auth failures (bad credentials, duplicate account, etc.)"""


class AuthService:
    def __init__(self):
        self.db = sqlite_db

    def register(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict:
        username = username.strip().lower()
        email = email.strip().lower()

        if self.db.get_user_by_username(username):
            raise AuthError("That username is already taken")
        if self.db.get_user_by_email(email):
            raise AuthError("An account with that email already exists")

        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
        }

        try:
            self.db.create_user(user)
        except sqlite3.IntegrityError:
            raise AuthError("That username or email is already registered")

        logger.info(f"👤 New user registered: {username}")
        return self.db.get_user_by_id(user["id"])

    def authenticate(self, identifier: str, password: str) -> Dict:
        identifier = identifier.strip().lower()
        user = self.db.get_user_by_username(identifier) or self.db.get_user_by_email(identifier)

        if not user or not verify_password(password, user["password_hash"]):
            raise AuthError("Incorrect username/email or password")

        return user

    def issue_token(self, user: Dict) -> str:
        return create_access_token(subject=user["id"], extra_claims={"username": user["username"]})

    def find_or_create_oauth_user(self, email: str, suggested_username: str, full_name: str = None) -> Dict:
        """
        Find an existing account by email, or create one for a first-time
        OAuth sign-in. OAuth accounts get an unusable random password hash --
        they can only ever sign in through the OAuth provider, never via
        username/password, which is the correct behavior (there's no password
        for them to have set).
        """
        email = email.strip().lower()

        existing = self.db.get_user_by_email(email)
        if existing:
            return existing

        username = self._unique_username(suggested_username)

        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": hash_password(str(uuid.uuid4())),  # unusable random password
            "full_name": full_name,
        }

        try:
            self.db.create_user(user)
        except sqlite3.IntegrityError:
            # Extremely unlikely race (email/username taken between check and insert) -- retry once.
            existing = self.db.get_user_by_email(email)
            if existing:
                return existing
            raise AuthError("Could not create account for this email")

        logger.info(f"👤 New OAuth user registered: {username}")
        return self.db.get_user_by_id(user["id"])

    def _unique_username(self, suggested: str) -> str:
        """Sanitize a suggested username and disambiguate if it's already taken."""
        base = "".join(c for c in suggested.lower().replace(" ", "_") if c.isalnum() or c == "_") or "user"
        candidate = base
        suffix = 0
        while self.db.get_user_by_username(candidate):
            suffix += 1
            candidate = f"{base}{suffix}"
        return candidate


# Singleton instance
auth_service = AuthService()