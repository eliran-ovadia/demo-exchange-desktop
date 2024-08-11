from PyQt5.QtWidgets import QMainWindow
from UI.Dashboard_ui import Ui_dashboard_ui

class DashboardApp(QMainWindow):
    def __init__(self, main_controller):
        super().__init__()
        self.ui = Ui_dashboard_ui()
        self.ui.setupUi(self)
        self.main_controller = main_controller