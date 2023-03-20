from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from ivviewer.ivcviewer import IvcViewer


class Viewer(QWidget):

    def __init__(self, parent=None, solid_axis_enabled: bool = True, grid_color: QColor = None,
                 back_color: QColor = None, text_color: QColor = None, color_for_rest_cursors: QColor = None,
                 color_for_selected_cursor: QColor = None, axis_label_enabled: bool = True, axis_font: QFont = None,
                 cursor_font: QFont = None, title_font: QFont = None, x_title: str = None, y_title: str = None,
                 x_label: str = None, y_label: str = None, accuracy: int = None) -> None:
        """
        :param parent: parent widget;
        :param solid_axis_enabled: if True then axes will be shown with solid lines;
        :param grid_color: grid color;
        :param back_color: canvas background color;
        :param text_color: color of text at the center of plot;
        :param color_for_rest_cursors: color for unselected cursors;
        :param color_for_selected_cursor: color for selected cursor.
        :param axis_label_enabled: if True then labels of axes will be displayed;
        :param axis_font: font for values on axes;
        :param cursor_font: font of text at cursors;
        :param title_font: axis titles font;
        :param x_title: title for horizontal axis;
        :param y_title: title for vertical axis;
        :param x_label: short name for horizontal axis;
        :param y_label: short name for vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursors.
        """

        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        self._plot = IvcViewer(self, solid_axis_enabled=solid_axis_enabled, grid_color=grid_color,
                               back_color=back_color, text_color=text_color,
                               color_for_rest_cursors=color_for_rest_cursors,
                               color_for_selected_cursor=color_for_selected_cursor,
                               axis_label_enabled=axis_label_enabled, axis_font=axis_font, cursor_font=cursor_font,
                               title_font=title_font, x_title=x_title, y_title=y_title, x_label=x_label,
                               y_label=y_label, accuracy=accuracy)
        self._plot.curves.clear()
        layout.addWidget(self._plot)

    @property
    def plot(self) -> IvcViewer:
        return self._plot
