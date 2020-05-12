from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from .ivcviewer import IvcViewer


class Viewer(QWidget):
    def __init__(self, parent=None):
        super(Viewer, self).__init__(parent=parent)

        layout = QVBoxLayout(self)

        self._plot = IvcViewer(self)
        layout.addWidget(self._plot)

    @property
    def plot(self):
        return self._plot
