import sys, os
import asyncio
import qasync
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt


def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def load_svg_pixmap(relative: str, width: int, height: int) -> QPixmap:
    renderer = QSvgRenderer(resource_path(relative))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _build_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(load_svg_pixmap("assets/icon.svg", size, size))
    return icon


def load_stylesheet(app: QApplication) -> None:
    with open(resource_path("styles/theme.qss"), "r") as f:
        app.setStyleSheet(f.read())


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Demo Exchange")
    app.setOrganizationName("DemoExchange")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(_build_app_icon())

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
