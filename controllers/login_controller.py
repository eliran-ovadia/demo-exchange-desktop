from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QThreadPool, pyqtSlot, Qt
from UI.login_ui import Ui_Login_window
from workers.auth_worker import AuthWorker
from widgets.loader import LoaderWidget
from design import Design

class LoginApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_Login_window()
        self.ui.setupUi(self)
        self.main_controller = main_controller
        self.thread_pool = QThreadPool()
        self.loader_widget = LoaderWidget("res/loader.gif", self, geometry=self.ui.login_button.geometry())
        self.ui.signup_button.clicked.connect(self.main_controller.show_signup_window)
        self.ui.login_button.clicked.connect(self.enter_dashboard)
        # Create a shortcut for Enter key
        self.enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.enter_shortcut.activated.connect(self.enter_dashboard)
        
    def enter_dashboard(self):
        if self.validate_inputs():
            self.perform_login()

    def validate_inputs(self):
        if not self.ui.email_input.text() or not self.ui.password_input.text():
            self.ui.login_button.setText("Fill in all fields")
            self.ui.login_button.setStyleSheet(Design.red_button_style)
            return False
        return True

    def perform_login(self):
        self.ui.login_button.hide()
        self.loader_widget.start()
        username = self.ui.email_input.text()
        password = self.ui.password_input.text()
        worker = AuthWorker(username, password)
        worker.signals.auth_complete.connect(self.on_auth_complete)
        self.thread_pool.start(worker)

    @pyqtSlot(bool, dict)
    def on_auth_complete(self, success, data):
        self.loader_widget.stop()
        if success:
            self.main_controller.show_dashboard_window()
        else:
            self.display_error("Credentials are incorrect")

    def display_error(self, message):
        self.ui.login_button.show()
        self.ui.login_button.setText(message)

