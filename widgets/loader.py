from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

class LoaderWidget(QLabel):
    def __init__(self, gif_file, parent=None, geometry=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(gif_file)
        self.setMovie(self.movie)
        self.setGeometry(geometry)
        self.hide()

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()
