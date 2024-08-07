import requests
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

class AuthWorkerSignals(QObject):
    auth_complete = pyqtSignal(bool, dict)

class AuthWorker(QRunnable):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.signals = AuthWorkerSignals()

    @pyqtSlot()
    def run(self):
        TOKEN_URL = "http://127.0.0.1:8000/token"
        payload = {
            'username': self.username,
            'password': self.password
        }

        try:
            response = requests.post(TOKEN_URL, data=payload)

            if response.status_code == 200:
                token_data = response.json()
                self.signals.auth_complete.emit(True, token_data)
            else:
                self.signals.auth_complete.emit(False, response.json())

        except requests.RequestException as e:
            self.signals.auth_complete.emit(False, {'error': str(e)})
