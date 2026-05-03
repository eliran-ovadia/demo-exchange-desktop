from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from PyQt5 import uic

import asyncio
from main import resource_path, load_svg_pixmap
from presenters.login_presenter import LoginPresenter


class LoginView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/login.ui"), self)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.registerButton.setFixedHeight(20)
        self.registerButton.setCursor(Qt.PointingHandCursor)
        self._load_logo()
        self._presenter = LoginPresenter(self)
        self._wire()

    def _load_logo(self) -> None:
        pixmap = load_svg_pixmap("assets/icon.svg", 72, 72)
        self.logoLabel.setPixmap(pixmap)
        self.logoLabel.setText("")
        self.logoLabel.setFixedSize(72, 72)
        self.logoLabel.setAlignment(Qt.AlignCenter)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    def _wire(self) -> None:
        self.loginButton.clicked.connect(self._on_login_clicked)
        self.registerButton.clicked.connect(self._on_register_clicked)
        self.passwordInput.returnPressed.connect(self._on_login_clicked)

    def _on_login_clicked(self) -> None:
        asyncio.ensure_future(self._presenter.handle_login())

    def _on_register_clicked(self) -> None:
        self._presenter.navigate_to_register()

    # ── Presenter API ──────────────────────────────────────────

    def get_email(self) -> str:
        return self.emailInput.text().strip()

    def get_password(self) -> str:
        return self.passwordInput.text()

    def set_loading(self, loading: bool) -> None:
        self.loginButton.setEnabled(not loading)
        self.loginButton.setText("Signing in…" if loading else "Sign In")
        self.emailInput.setEnabled(not loading)
        self.passwordInput.setEnabled(not loading)

    def show_error(self, message: str) -> None:
        self.errorLabel.setText(message)

    def clear_error(self) -> None:
        self.errorLabel.setText("")

    def navigate_to_dashboard(self, email: str = "") -> None:
        from views.main_window_view import MainWindowView
        self._main = MainWindowView()
        if email:
            self._main.set_user_email(email)
        self._main.show()
        self.close()
