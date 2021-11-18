from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from .ivcviewer import IvcViewer


class Viewer(QWidget):
    def __init__(self, parent=None, solid_axis_enabled: bool = True,
                 grid_color: QColor = QColor(0, 0, 0),
                 back_color: QColor = QColor(0xe1, 0xed, 0xeb),
                 text_color: QColor = QColor(255, 0, 0), axis_sign_enabled: bool = True):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        self._plot = IvcViewer(self, grid_color=grid_color, back_color=back_color,
                               solid_axis_enabled=solid_axis_enabled, text_color=text_color,
                               axis_sign_enabled=axis_sign_enabled, axis_font_size=15,
                               title_font_size=30)
        self._plot.curves.clear()
        layout.addWidget(self._plot)

    @property
    def plot(self):
        return self._plot
