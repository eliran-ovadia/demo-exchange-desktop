from controllers.login_controller import LoginApp
from controllers.signup_controller import SignupApp
from controllers.dashboard_controller import DashboardApp
from controllers.signup_success_popup import SignupSuccessPopup



class MainController:
    def __init__(self):
        self.current_window = None

    def show_login_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = LoginApp(self)
        self.current_window.show()

    def show_signup_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = SignupApp(self)
        self.current_window.show()
        
    def show_dashboard_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = DashboardApp(self)
        self.current_window.show()
    
    def show_signup_success_popup(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = SignupSuccessPopup(self)
        self.current_window.show()
