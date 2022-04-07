from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from .ivcviewer import (DEFAULT_AXIS_FONT, DEFAULT_MARKER_FONT, DEFAULT_SCREENSHOT_FILE_NAME_BASE, DEFAULT_TITLE_FONT,
                        IvcViewer)


class Viewer(QWidget):
    def __init__(self, parent=None, solid_axis_enabled: bool = True, grid_color: QColor = QColor(0, 0, 0),
                 back_color: QColor = QColor(0xe1, 0xed, 0xeb), text_color: QColor = QColor(255, 0, 0),
                 color_for_rest_markers: QColor = QColor(102, 255, 0),
                 color_for_selected_marker: QColor = QColor(255, 0, 0), axis_sign_enabled: bool = True,
                 axis_font: QFont = DEFAULT_AXIS_FONT, marker_font: QFont = DEFAULT_MARKER_FONT,
                 title_font: QFont = DEFAULT_TITLE_FONT,
                 screenshot_file_name_base: str = DEFAULT_SCREENSHOT_FILE_NAME_BASE):
        """
        :param parent: parent widget;
        :param solid_axis_enabled: if True then axes will be shown with solid lines;
        :param grid_color: grid color;
        :param back_color: canvas background color;
        :param text_color: color of text at center of plot;
        :param color_for_rest_markers: color for unselected cursors;
        :param color_for_selected_marker: color for selected cursor.
        :param axis_sign_enabled: if True then labels of axes will be displayed;
        :param axis_font: font for values on axes;
        :param marker_font: font of text at markers;
        :param title_font: axis titles font;
        :param screenshot_file_name_base: base name for screenshot files.
        """

        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        self._plot = IvcViewer(self, grid_color=grid_color, back_color=back_color,
                               solid_axis_enabled=solid_axis_enabled, text_color=text_color,
                               color_for_rest_markers=color_for_rest_markers,
                               color_for_selected_marker=color_for_selected_marker, axis_sign_enabled=axis_sign_enabled,
                               axis_font=axis_font, marker_font=marker_font, title_font=title_font,
                               screenshot_file_name_base=screenshot_file_name_base)
        self._plot.curves.clear()
        layout.addWidget(self._plot)

    @property
    def plot(self):
        return self._plot
