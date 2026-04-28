import sys
import asyncio
import qasync
from PyQt5.QtWidgets import QApplication


def load_stylesheet(app: QApplication) -> None:
    with open("styles/theme.qss", "r") as f:
        app.setStyleSheet(f.read())


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Demo Exchange")
    app.setOrganizationName("DemoExchange")
    app.setApplicationVersion("1.0.0")

    load_stylesheet(app)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Import after event loop is set
    from services.auth_service import auth_service

    if auth_service.restore_session():
        from views.main_window_view import MainWindowView
        window = MainWindowView()
        window.set_user_email(auth_service.load_email())
    else:
        from views.login_view import LoginView
        window = LoginView()

    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
