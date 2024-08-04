from PyQt5.QtWidgets import QMainWindow
from UI.login_ui import Ui_Login_window

class LoginApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_Login_window()
        self.ui.setupUi(self)
        self.main_controller = main_controller
        self.ui.signup_button.clicked.connect(self.main_controller.show_signup_window)
