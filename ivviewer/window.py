from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from .ivcviewer import DEFAULT_AXIS_FONT, DEFAULT_MARKER_FONT, DEFAULT_TITLE_FONT, IvcViewer


class Viewer(QWidget):
    def __init__(self, parent=None, solid_axis_enabled: bool = True,
                 grid_color: QColor = QColor(0, 0, 0),
                 back_color: QColor = QColor(0xe1, 0xed, 0xeb),
                 text_color: QColor = QColor(255, 0, 0), axis_sign_enabled: bool = True,
                 axis_font: QFont = DEFAULT_AXIS_FONT, marker_font: QFont = DEFAULT_MARKER_FONT,
                 title_font: QFont = DEFAULT_TITLE_FONT):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        self._plot = IvcViewer(self, grid_color=grid_color, back_color=back_color,
                               solid_axis_enabled=solid_axis_enabled, text_color=text_color,
                               axis_sign_enabled=axis_sign_enabled, axis_font=axis_font,
                               marker_font=marker_font, title_font=title_font)
        self._plot.curves.clear()
        layout.addWidget(self._plot)

    @property
    def plot(self):
        return self._plot
