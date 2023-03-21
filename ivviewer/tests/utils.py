import sys
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QApplication
from ivviewer import Viewer


def prepare_test(test_func):
    """
    Decorator prepares viewer widget and checks if it needs to be displayed.
    :param test_func: decorated function.
    """

    def wrapper(self, display_window: bool):
        """
        :param self:
        :param display_window: if True then widget will be displayed.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)

        test_func(self, window)

        if display_window:
            window.show()
            app.exec()
    return wrapper


class MouseEvent:

    def __init__(self, pos: QPoint) -> None:
        self._pos = pos

    def accept(self) -> None:
        pass

    def button(self) -> int:
        return Qt.LeftButton

    def pos(self) -> QPoint:
        return self._pos
