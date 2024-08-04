from PyQt5.QtWidgets import QMainWindow
from UI.signup_ui import Ui_Signup_window

class SignupApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_Signup_window()
        self.ui.setupUi(self)
        self.main_controller = main_controller
        self.ui.login_button.clicked.connect(self.main_controller.show_login_window)
