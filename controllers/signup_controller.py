from PyQt5.QtWidgets import QMainWindow
from widgets.loader import LoaderWidget
from PyQt5.QtCore import QThreadPool, pyqtSlot
from UI.signup_ui import Ui_Signup_window
from workers.create_user_worker import CreateUserWorker
from design import Design

class SignupApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_Signup_window()
        self.ui.setupUi(self)
        self.main_controller = main_controller
        self.thread_pool = QThreadPool()
        self.loader_widget = LoaderWidget("res/loader.gif", self, geometry=self.ui.signup_button.geometry())
        self.ui.login_button.clicked.connect(self.main_controller.show_login_window)
        self.ui.signup_button.clicked.connect(self.return_to_login)

    def return_to_login(self):
        if self.validate_inputs():
            self.perform_signup()

    def validate_inputs(self):
        if not self.ui.email_input.text() or not self.ui.password_input.text() or not self.ui.first_name_input.text() or not self.ui.last_name_input.text():
            self.ui.signup_button.setText("Fill in all fields")
            self.ui.signup_button.setStyleSheet(Design.red_button_style)
            return False
        return True

    def perform_signup(self):
        self.ui.login_button.hide()
        self.loader_widget.start()
        username = self.ui.email_input.text()
        password = self.ui.password_input.text()
        first_name = self.ui.first_name_input.text()
        last_name = self.ui.last_name_input.text()
        worker = CreateUserWorker(username, password, first_name, last_name)
        worker.signals.signup_complete.connect(self.on_signup_complete)
        self.thread_pool.start(worker)

    @pyqtSlot(bool, dict)
    def on_signup_complete(self, success, data):
        self.loader_widget.stop()
        if success:
            self.main_controller.show_login_window()
        else:
            self.display_error("There was a problem") #add logic to indicate used email

    def display_error(self, message):
        self.ui.login_button.show()
        self.ui.login_button.setText(message)
