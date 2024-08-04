import requests
from PyQt5.QtWidgets import QMainWindow
from UI.login_ui import Ui_Login_window

class LoginApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_Login_window()
        self.ui.setupUi(self)
        self.main_controller = main_controller
        self.ui.signup_button.clicked.connect(self.main_controller.show_signup_window)
        self.ui.login_button.clicked.connect(self.enter_dashboard)
    
    def enter_dashboard(self):
        if self.authenticate():
            self.main_controller.show_dashboard_window()
    
    def authenticate(self) -> bool:
        TOKEN_URL = "http://127.0.0.1:8000/token"
        
        payload = {
            'username': self.ui.email_input.text(),
            'password': self.ui.password_input.text()
        }
        
        try:
            response = requests.post(TOKEN_URL, data=payload)

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                token_type = token_data.get('token_type', 'Bearer')
                print(f"Token Type: {token_type}")
                print(f"Access Token: {access_token}")
                return True
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.json()}")
                return False
                
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            return False