from __future__ import annotations

import logging
from services.auth_service import auth_service
from services.api_client import APIError

logger = logging.getLogger(__name__)

if False:  # TYPE_CHECKING
    from views.login_view import LoginView


class LoginPresenter:
    def __init__(self, view: "LoginView") -> None:
        self._view = view

    async def handle_login(self) -> None:
        email = self._view.get_email()
        password = self._view.get_password()

        if not email:
            self._view.show_error("Please enter your email address.")
            return
        if not password:
            self._view.show_error("Please enter your password.")
            return

        self._view.clear_error()
        self._view.set_loading(True)
        logger.debug("Login attempt: %s", email)

        try:
            await auth_service.login(email, password)
            logger.info("Login successful: %s", email)
            self._view.navigate_to_dashboard(email)
        except APIError as e:
            if e.status_code == 401:
                logger.warning("Login rejected (401): %s", email)
                self._view.show_error("Invalid email or password.")
            else:
                logger.warning("Login API error %s: %s", e.status_code, e.detail)
                self._view.show_error(f"Login failed: {e.detail}")
        except Exception as e:
            logger.error("Login unexpected error", exc_info=True)
            self._view.show_error(f"Could not connect to server: {e}")
        finally:
            self._view.set_loading(False)

    def navigate_to_register(self) -> None:
        from views.register_view import RegisterView
        self._register = RegisterView()
        self._register.show()
        self._view.close()
