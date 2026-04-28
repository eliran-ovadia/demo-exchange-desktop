from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from PyQt5 import uic

from main import resource_path
from presenters.register_presenter import RegisterPresenter


class RegisterView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/register.ui"), self)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.backButton.setFixedHeight(20)
        self.backButton.setCursor(Qt.PointingHandCursor)
        self._presenter = RegisterPresenter(self)
        self._wire()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    def _wire(self) -> None:
        self.createButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.handle_register())
        )
        self.backButton.clicked.connect(self._presenter.navigate_to_login)
        self.confirmInput.returnPressed.connect(
            lambda: asyncio.ensure_future(self._presenter.handle_register())
        )

    # ── Presenter API ──────────────────────────────────────────

    def get_fields(self) -> dict:
        return {
            "name": self.firstNameInput.text().strip(),
            "last_name": self.lastNameInput.text().strip(),
            "email": self.emailInput.text().strip(),
            "password": self.passwordInput.text(),
            "password_confirm": self.confirmInput.text(),
        }

    def set_loading(self, loading: bool) -> None:
        self.createButton.setEnabled(not loading)
        self.createButton.setText("Creating account…" if loading else "Create Account")
        for w in (self.firstNameInput, self.lastNameInput,
                  self.emailInput, self.passwordInput, self.confirmInput):
            w.setEnabled(not loading)

    def show_error(self, message: str) -> None:
        self.errorLabel.setText(message)
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.style().unpolish(self.errorLabel)
        self.errorLabel.style().polish(self.errorLabel)

    def show_success(self, message: str) -> None:
        self.errorLabel.setText(message)
        self.errorLabel.setObjectName("successLabel")
        self.errorLabel.style().unpolish(self.errorLabel)
        self.errorLabel.style().polish(self.errorLabel)

    def clear_error(self) -> None:
        self.errorLabel.setText("")

    def navigate_to_login(self) -> None:
        from views.login_view import LoginView
        self._login = LoginView()
        self._login.show()
        self.close()
