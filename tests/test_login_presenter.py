from unittest.mock import MagicMock, AsyncMock, call, patch

from presenters.login_presenter import LoginPresenter
from services.api_client import APIError


def make_view(email="user@example.com", password="secret"):
    view = MagicMock()
    view.get_email.return_value = email
    view.get_password.return_value = password
    return view


# ── Validation ────────────────────────────────────────────

async def test_empty_email_shows_error_and_never_calls_api():
    view = make_view(email="")
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock()
        await presenter.handle_login()
    view.show_error.assert_called_once_with("Please enter your email address.")
    mock_auth.login.assert_not_called()
    view.set_loading.assert_not_called()


async def test_empty_password_shows_error_and_never_calls_api():
    view = make_view(password="")
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock()
        await presenter.handle_login()
    view.show_error.assert_called_once_with("Please enter your password.")
    mock_auth.login.assert_not_called()


# ── Success ───────────────────────────────────────────────

async def test_successful_login_navigates_to_dashboard():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock()
        await presenter.handle_login()
    view.navigate_to_dashboard.assert_called_once_with("user@example.com")
    view.show_error.assert_not_called()


async def test_loading_state_always_reset_after_success():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock()
        await presenter.handle_login()
    assert view.set_loading.call_args_list == [call(True), call(False)]


# ── API errors ────────────────────────────────────────────

async def test_401_shows_invalid_credentials_message():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock(side_effect=APIError(401, "Unauthorized"))
        await presenter.handle_login()
    view.show_error.assert_called_with("Invalid email or password.")
    view.navigate_to_dashboard.assert_not_called()


async def test_500_shows_api_error_detail():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock(side_effect=APIError(500, "Internal Server Error"))
        await presenter.handle_login()
    view.show_error.assert_called_with("Login failed: Internal Server Error")


async def test_network_error_shows_friendly_message():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock(
            side_effect=APIError(0, "Could not reach server. Check your connection.")
        )
        await presenter.handle_login()
    view.show_error.assert_called_with(
        "Login failed: Could not reach server. Check your connection."
    )


async def test_loading_state_always_reset_after_error():
    view = make_view()
    presenter = LoginPresenter(view)
    with patch("presenters.login_presenter.auth_service") as mock_auth:
        mock_auth.login = AsyncMock(side_effect=APIError(401, "Unauthorized"))
        await presenter.handle_login()
    assert view.set_loading.call_args_list == [call(True), call(False)]
