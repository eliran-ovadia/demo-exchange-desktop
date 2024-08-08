import requests
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

class CreateUserSignals(QObject):
    signup_complete = pyqtSignal(bool, dict)

class CreateUserWorker(QRunnable):
    def __init__(self, email, password, first_name, last_name):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.signals = CreateUserSignals()

    @pyqtSlot()
    def run(self):
        URL = "http://127.0.0.1:8000/createUser"
        payload = {
            'name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password
        }

        try:
            response = requests.post(URL, data=payload)

            if response.status_code == 201:
                confirmed_email = response.json()
                self.signals.signup_complete.emit(True, confirmed_email)
            else:
                self.signals.signup_complete.emit(False, response.json())

        except requests.RequestException as e:
            self.signals.signup_complete.emit(False, {'error': str(e)})
    