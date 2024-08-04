from PyQt5.QtWidgets import QApplication
from controllers.main_controller import MainController

def main():
    app = QApplication([])
    controller = MainController()
    controller.show_login_window()
    app.exit(app.exec_())

if __name__ == "__main__":
    main()
