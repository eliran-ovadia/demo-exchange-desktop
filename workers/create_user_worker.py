import requests
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QRunnable

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
        URL = "http://127.0.0.1:8000/api/createUser"
        payload = {
            'name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password
        }

        try:
            response = requests.post(URL, json=payload)


            response_data = response.json()

            if response.status_code == 201:
                self.signals.signup_complete.emit(True, {'detail': "Signed up succesfuly!"})
            else:
                detail_message = response_data.get('detail', 'An unknown error occurred')

                if isinstance(detail_message, list):
                    if detail_message:
                        detail_message = detail_message[0].get('msg', 'An error has occurred')
                    else:
                        detail_message = 'An error has occurred'

                elif isinstance(detail_message, dict):
                    detail_message = detail_message.get('msg', 'An error has occurred')
                
                self.signals.signup_complete.emit(False, {'detail': detail_message})

        except requests.RequestException as e:
            print(e)
            self.signals.signup_complete.emit(False, {'error': "An error has occurred"})
