from PyQt5.QtWidgets import QApplication
import sys
from .window import Viewer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Viewer()
    window.show()
    app.exec()
