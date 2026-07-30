"""Google & GitHub OAuth helpers.

Handles building the provider consent-screen URLs and exchanging an
authorization code for the user's profile info. Kept separate from the
route layer so the HTTP/token-exchange details aren't mixed into
app/api/routes/oauth.py.
"""

import httpx

from app.core.config import settings
from app.core.logger import logger


class OAuthError(Exception):
    """Raised for expected OAuth failures (bad code, provider error, etc.)"""


# ---- Google ----

def get_google_auth_url() -> str:
    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline&prompt=consent"
    )


async def get_google_user_info(code: str) -> dict:
    """Exchange an authorization code for the user's Google profile."""
    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_res.status_code != 200:
            logger.error(f"❌ Google token exchange failed: {token_res.text}")
            raise OAuthError("Could not exchange Google authorization code")

        access_token = token_res.json().get("access_token")
        if not access_token:
            raise OAuthError("Google did not return an access token")

        userinfo_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_res.status_code != 200:
            logger.error(f"❌ Google userinfo fetch failed: {userinfo_res.text}")
            raise OAuthError("Could not fetch Google profile")

        data = userinfo_res.json()

    if not data.get("email"):
        raise OAuthError("Google account has no email address")

    return {
        "email": data["email"],
        "name": data.get("name") or data["email"].split("@")[0],
    }


# ---- GitHub ----

def get_github_auth_url() -> str:
    return (
        "https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        "&scope=read:user%20user:email"
    )


async def get_github_user_info(code: str) -> dict:
    """Exchange an authorization code for the user's GitHub profile."""
    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "code": code,
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        if token_res.status_code != 200:
            logger.error(f"❌ GitHub token exchange failed: {token_res.text}")
            raise OAuthError("Could not exchange GitHub authorization code")

        token_payload = token_res.json()
        access_token = token_payload.get("access_token")
        if not access_token:
            logger.error(f"❌ GitHub token response missing access_token: {token_payload}")
            raise OAuthError(token_payload.get("error_description", "GitHub did not return an access token"))

        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}

        user_res = await client.get("https://api.github.com/user", headers=headers)
        if user_res.status_code != 200:
            logger.error(f"❌ GitHub user fetch failed: {user_res.text}")
            raise OAuthError("Could not fetch GitHub profile")
        user_data = user_res.json()

        # GitHub only includes `email` in /user if the user made it public.
        # Fall back to the emails endpoint to get their primary verified email.
        email = user_data.get("email")
        if not email:
            emails_res = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_res.status_code == 200:
                emails = emails_res.json()
                primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
                if not primary:
                    primary = next((e for e in emails if e.get("verified")), None)
                email = primary["email"] if primary else None

    if not email:
        raise OAuthError(
            "Your GitHub account has no accessible email address. "
            "Add a public or verified email at github.com/settings/emails and try again."
        )

    return {
        "email": email,
        "username": user_data.get("login"),
        "name": user_data.get("name") or user_data.get("login"),
    }