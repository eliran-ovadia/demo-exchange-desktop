from PyQt5.QtWidgets import QWidget
from UI.signup_success_popup_ui import Ui_Signuo_success_popup

class SignupSuccessPopup(QWidget):
    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.ui = Ui_Signuo_success_popup()
        self.ui.setupUi(self)
        self.ui.login_button.clicked.connect(self.main_controller.show_login_window)