from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QColor

from .ivcviewer import IvcViewer


class Viewer(QWidget):
    def __init__(self, parent=None):
        super(Viewer, self).__init__(parent=parent)

        layout = QVBoxLayout(self)

        self._plot = IvcViewer(self, grid_color=QColor(255, 255, 255), back_color=QColor(0, 0, 0))
        layout.addWidget(self._plot)

    @property
    def plot(self):
        return self._plot
