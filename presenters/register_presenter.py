from __future__ import annotations

import asyncio
import logging
from services.api_client import api_client, APIError

logger = logging.getLogger(__name__)

if False:
    from views.register_view import RegisterView


class RegisterPresenter:
    def __init__(self, view: "RegisterView") -> None:
        self._view = view

    async def handle_register(self) -> None:
        fields = self._view.get_fields()

        if not fields["name"]:
            self._view.show_error("First name is required.")
            return
        if not fields["last_name"]:
            self._view.show_error("Last name is required.")
            return
        if not fields["email"]:
            self._view.show_error("Email is required.")
            return
        if not fields["password"]:
            self._view.show_error("Password is required.")
            return
        if fields["password"] != fields["password_confirm"]:
            self._view.show_error("Passwords do not match.")
            return

        self._view.clear_error()
        self._view.set_loading(True)
        logger.debug("Register attempt: %s", fields["email"])
        try:
            await api_client.register(
                name=fields["name"],
                last_name=fields["last_name"],
                email=fields["email"],
                password=fields["password"],
                password_confirm=fields["password_confirm"],
            )
            logger.info("Registration successful: %s", fields["email"])
            self._view.show_success("Account created! Redirecting to sign in…")
            await asyncio.sleep(1.2)
            self._view.navigate_to_login()
        except APIError as e:
            detail = e.detail
            if isinstance(detail, list):
                detail = detail[0].get("msg", str(detail)) if detail else "Validation error."
            logger.warning("Register API error %s: %s", e.status_code, e.detail)
            self._view.show_error(str(detail))
        except Exception as e:
            logger.error("Register unexpected error", exc_info=True)
            self._view.show_error(f"Could not connect to server: {e}")
        finally:
            self._view.set_loading(False)

    def navigate_to_login(self) -> None:
        self._view.navigate_to_login()
