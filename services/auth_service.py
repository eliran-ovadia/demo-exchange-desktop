from __future__ import annotations

import keyring
from services.api_client import api_client, APIError

_SERVICE = "demo-exchange"
_ACCESS_KEY = "access_token"
_REFRESH_KEY = "refresh_token"
_EMAIL_KEY = "email"


class AuthService:
    """Manages token lifecycle: store, load, refresh, and logout."""

    def load_tokens(self) -> tuple[str | None, str | None]:
        access = keyring.get_password(_SERVICE, _ACCESS_KEY)
        refresh = keyring.get_password(_SERVICE, _REFRESH_KEY)
        return access, refresh

    def save_tokens(self, access_token: str, refresh_token: str) -> None:
        keyring.set_password(_SERVICE, _ACCESS_KEY, access_token)
        keyring.set_password(_SERVICE, _REFRESH_KEY, refresh_token)
        api_client.set_token(access_token)

    def clear_tokens(self) -> None:
        for key in (_ACCESS_KEY, _REFRESH_KEY, _EMAIL_KEY):
            try:
                keyring.delete_password(_SERVICE, key)
            except Exception:
                pass
        api_client.clear_token()

    async def login(self, email: str, password: str) -> None:
        data = await api_client.login(email, password)
        self.save_tokens(data["access_token"], data["refresh_token"])
        keyring.set_password(_SERVICE, _EMAIL_KEY, email)

    async def refresh(self) -> bool:
        """Try to exchange the stored refresh token for a new pair. Returns True on success."""
        _, refresh_token = self.load_tokens()
        if not refresh_token:
            return False
        try:
            data = await api_client.refresh(refresh_token)
            self.save_tokens(data["access_token"], data["refresh_token"])
            return True
        except APIError:
            self.clear_tokens()
            return False

    async def logout(self) -> None:
        _, refresh_token = self.load_tokens()
        if refresh_token:
            try:
                await api_client.logout(refresh_token)
            except APIError:
                pass
        self.clear_tokens()

    def load_email(self) -> str:
        return keyring.get_password(_SERVICE, _EMAIL_KEY) or ""

    def restore_session(self) -> bool:
        """Load tokens from keyring and arm the API client. Returns True if tokens exist."""
        access, _ = self.load_tokens()
        if access:
            api_client.set_token(access)
            return True
        return False


auth_service = AuthService()
# Register the refresh hook so api_client can silently retry on 401
api_client.set_refresh_hook(auth_service.refresh)
