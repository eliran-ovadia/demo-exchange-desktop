import sys
import asyncio
import qasync
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


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

    # Import here so the event loop is already set when views initialize
    from views.login_view import LoginView

    window = LoginView()
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
