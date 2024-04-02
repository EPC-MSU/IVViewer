from typing import List, Optional, Union
import numpy as np
from PyQt5.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen, QPainter
from qwt import QwtPlot, QwtPlotMarker, QwtText
from qwt.scale_map import QwtScaleMap
from ivviewer.curve import Point


class IvcCursor(QwtPlotMarker):
    """
    This class is cursor with horizontal and vertical lines, it shows coordinates for selected point.
    """

    CROSS_SIZE: int = 10  # default size of white cross in px
    DEFAULT_FONT_SIZE: int = 10
    DEFAULT_PEN_WIDTH: int = 2
    DEFAULT_X_LABEL: str = "U"
    DEFAULT_Y_LABEL: str = "I"

    def __init__(self, pos: Point, ivc_viewer: QwtPlot, font: Optional[QFont] = None, x_label: Optional[str] = None,
                 y_label: Optional[str] = None, accuracy: Optional[int] = None) -> None:
        """
        :param pos: point at which to place cursor;
        :param ivc_viewer: plot on which to place cursor;
        :param font: font of text at cursor;
        :param x_label: name of the horizontal axis;
        :param y_label: name of the vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursor.
        """

        super().__init__()
        self._accuracy: int = accuracy
        self._font: QFont = font if isinstance(font, QFont) else QFont("", IvcCursor.DEFAULT_FONT_SIZE)
        self._ivc_viewer: QwtPlot = ivc_viewer
        self._pen_for_cross: QPen = QPen(QBrush(QColor(255, 255, 255)), IvcCursor.DEFAULT_PEN_WIDTH)
        self._x_label: str = x_label if x_label else IvcCursor.DEFAULT_X_LABEL
        self._y_label: str = y_label if y_label else IvcCursor.DEFAULT_Y_LABEL

        cursor_text = QwtText()
        cursor_text.setFont(self._font)
        cursor_text.setRenderFlags(Qt.AlignLeft)
        self._marker: QwtPlotMarker = QwtPlotMarker()
        self.setSpacing(5)
        self.setLineStyle(QwtPlotMarker.Cross)
        self.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self.setLabel(cursor_text)
        self.move(pos)

    @property
    def cursor_text(self) -> str:
        """
        :return: text to display on the cursor.
        """

        if isinstance(self._accuracy, int):
            x_value = format(self.value().x(), f".{self._accuracy}f")
            y_value = format(self.value().y(), f".{self._accuracy}f")
        else:
            x_value = self.value().x()
            y_value = self.value().y()
        return f"{self._x_label} = {x_value}, {self._y_label} = {y_value}"

    def _draw_cross(self, painter: QPainter, pos: QPointF) -> None:
        """
        :param painter: painter;
        :param pos: position where to draw a cross.
        """

        painter.setPen(self._pen_for_cross)
        painter.setRenderHint(QPainter.Antialiasing, False)
        x_1 = pos.x() - IvcCursor.CROSS_SIZE
        x_2 = pos.x() + IvcCursor.CROSS_SIZE
        y = pos.y()
        painter.drawLine(x_1, y, x_2, y)
        x = pos.x()
        y_1 = pos.y() - IvcCursor.CROSS_SIZE
        y_2 = pos.y() + IvcCursor.CROSS_SIZE
        painter.drawLine(x, y_1, x, y_2)

    @staticmethod
    def _get_brush(param: Union[QBrush, QColor, QPen]) -> QBrush:
        """
        :param param: parameter with which to get the brush.
        :return: brush.
        """

        if isinstance(param, QColor):
            brush = QBrush(param)
        elif isinstance(param, QBrush):
            brush = param
        elif isinstance(param, QPen):
            brush = param.brush()
        else:
            raise TypeError("Invalid type of argument passed. Allowed types: QBrush, QColor and QPen")
        return brush

    @staticmethod
    def _get_color(param: Union[QBrush, QColor, QPen]) -> QColor:
        """
        :param param: parameter with which to get the color.
        :return: color.
        """

        if isinstance(param, QColor):
            color = param
        elif isinstance(param, QBrush):
            color = param.color()
        elif isinstance(param, QPen):
            color = param.color()
        else:
            raise TypeError("Invalid type of argument passed. Allowed types: QBrush, QColor and QPen")
        return color

    @staticmethod
    def _get_pen(param: Union[QBrush, QColor, QPen]) -> QPen:
        """
        :param param: parameter with which to get the pen.
        :return: pen.
        """

        if isinstance(param, QColor):
            pen = QPen(QBrush(param), IvcCursor.DEFAULT_PEN_WIDTH, Qt.DotLine)
        elif isinstance(param, QBrush):
            pen = QPen(param, IvcCursor.DEFAULT_PEN_WIDTH, Qt.DotLine)
        elif isinstance(param, QPen):
            pen = param
        else:
            raise TypeError("Invalid type of argument passed. Allowed types: QBrush, QColor and QPen")
        return pen

    def attach(self, ivc_viewer: QwtPlot) -> None:
        """
        :param ivc_viewer: plot to which to attach a label.
        """

        self._ivc_viewer = ivc_viewer
        super().attach(self._ivc_viewer)

    def draw(self, painter: QPainter, x_map: QwtScaleMap, y_map: QwtScaleMap, canvas_rect: QRectF) -> None:
        """
        Method draws the marker.
        :param painter: painter;
        :param x_map: X scale map;
        :param y_map: Y scale map;
        :param canvas_rect: contents rectangle of the canvas in painter coordinates.
        """

        data = self._QwtPlotMarker__data
        pos = QPointF(x_map.transform(data.xValue), y_map.transform(data.yValue))
        self.drawLines(painter, canvas_rect, pos)
        self._draw_cross(painter, pos)
        self.drawLabel(painter, canvas_rect, pos)

    def get_cursor_coordinates_in_px(self) -> QPoint:
        """
        :return:
        """

        x = self._ivc_viewer.transform(QwtPlot.xBottom, self.value().x()) + self._ivc_viewer.canvas().x()
        y = self._ivc_viewer.transform(QwtPlot.yLeft, self.value().y()) + self._ivc_viewer.canvas().y()
        return QPoint(x, y)

    def move(self, pos: Point) -> None:
        """
        :param pos: position where to move the cursor.
        """

        self.setValue(pos.x, pos.y)
        self.label().setText(self.cursor_text)

    def paint(self, param: Union[QBrush, QColor, QPen], param_for_cross: Union[QBrush, QColor, QPen] = None) -> None:
        """
        Method draws all parts of cursor with given color, brush or pen.
        :param param: brush, color or pen for cursor;
        :param param_for_cross: brush, color or pen for cross in the cursor center.
        """

        color = self._get_color(param)
        self.label().setColor(color)
        pen = self._get_pen(param)
        self.setLinePen(pen)
        if param_for_cross:
            self._pen_for_cross = self._get_pen(param_for_cross)

    def set_axis_labels(self, x_label: str, y_label: str) -> None:
        """
        :param x_label: label for horizontal axis;
        :param y_label: label for vertical axis.
        """

        if x_label:
            self._x_label = x_label
        if y_label:
            self._y_label = y_label
        self.label().setText(self.cursor_text)


class IvcCursors:
    """
    This class is array of objects of class IvcCursor.
    """

    COLOR_FOR_REST: QColor = QColor(102, 255, 0)
    COLOR_FOR_SELECTED: QColor = QColor(255, 0, 0)
    DISTANCE_FOR_SELECTION: int = 3

    def __init__(self, ivc_viewer: QwtPlot, font: Optional[QFont] = None, color_for_rest: Optional[QColor] = None,
                 color_for_selected: Optional[QColor] = None, x_label: Optional[str] = None,
                 y_label: Optional[str] = None, accuracy: Optional[int] = None) -> None:
        """
        :param ivc_viewer: plot on which to place cursors;
        :param font: font of text at cursors;
        :param color_for_rest: color for unselected cursors;
        :param color_for_selected: color for selected cursor;
        :param x_label: name of the horizontal axis;
        :param y_label: name of the vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursors.
        """

        self._accuracy: int = accuracy
        self._color_for_rest: QColor = color_for_rest if isinstance(color_for_rest, QColor) else self.COLOR_FOR_REST
        self._color_for_selected: QColor = color_for_selected if isinstance(color_for_selected, QColor) else \
            self.COLOR_FOR_SELECTED
        self._current_index: int = None
        self._cursors: List[IvcCursor] = []
        self._font: QFont = font
        self._ivc_viewer: QwtPlot = ivc_viewer
        self._x_label: Optional[str] = x_label
        self._y_label: Optional[str] = y_label

    def __getitem__(self, index: int) -> Optional[IvcCursor]:
        """
        :param index: index of the cursor to be returned.
        :return: cursor.
        """

        if isinstance(index, int) and 0 <= index < len(self.cursors):
            return self._cursors[index]

        return None

    @property
    def cursors(self) -> List[IvcCursor]:
        """
        :return: list of all cursors.
        """

        return self._cursors

    def add_cursor(self, pos: Point) -> None:
        """
        Method adds cursor at given position.
        :param pos: position where cursor should be added.
        """

        _ = [cursor.paint(self._color_for_rest) for cursor in self._cursors]
        cursor = IvcCursor(pos, self._ivc_viewer, self._font, self._x_label, self._y_label, self._accuracy)
        cursor.paint(self._color_for_selected)
        cursor.attach(self._ivc_viewer)
        self._cursors.append(cursor)
        self._current_index = len(self._cursors) - 1

    def attach(self, ivc_viewer: QwtPlot) -> None:
        """
        Method attaches all cursors to plot.
        :param ivc_viewer: plot.
        """

        self._ivc_viewer = ivc_viewer
        _ = [cursor.attach(ivc_viewer) for cursor in self._cursors]

    def detach(self) -> None:
        """
        Method detaches all cursors from plot.
        """

        _ = [cursor.detach() for cursor in self._cursors]

    def find_cursor_at_point(self, pos: QPoint) -> Optional[int]:
        """
        :param pos: position where to find the cursor.
        :return: cursor index, at given position.
        """

        def get_distance(pos_1: QPoint, pos_2: QPoint) -> float:
            return np.sqrt((pos_1.x() - pos_2.x())**2 + (pos_1.y() - pos_2.y())**2)

        min_distance = None
        cursor_index = None
        for index, cursor in enumerate(self._cursors):
            cursor_pos = cursor.get_cursor_coordinates_in_px()
            distance = get_distance(pos, cursor_pos)
            if distance <= self.DISTANCE_FOR_SELECTION:
                if min_distance is None or min_distance > distance:
                    min_distance = distance
                    cursor_index = index
        return cursor_index

    def find_cursor_for_context_menu(self, pos: QPoint) -> bool:
        """
        Method finds cursor at given point for context menu work.
        :param pos: point next to which you want to search for the cursor.
        :return: True if cursor at given position was found otherwise False.
        """

        cursor_index = self.find_cursor_at_point(pos)
        if cursor_index is not None:
            self._current_index = cursor_index
            self.paint_current_cursor()
            return True

        return False

    def get_list_of_all_cursors(self) -> List[IvcCursor]:
        """
        Method returns list with all cursors.
        :return: list with all cursors.
        """

        return self._cursors

    def is_empty(self) -> bool:
        """
        Method checks if there are cursors.
        :return: True if object has no cursors otherwise False.
        """

        return not bool(self._cursors)

    def move_cursor(self, pos: Point) -> None:
        """
        Method moves current selected cursor at given position.
        :param pos: position to move.
        """

        if self._current_index is not None:
            self._cursors[self._current_index].move(pos)

    def paint_current_cursor(self) -> None:
        _ = [cursor.paint(self._color_for_rest) for cursor in self._cursors]
        if self._current_index is not None:
            self._cursors[self._current_index].paint(self._color_for_selected)

    def remove_all_cursors(self) -> None:
        """
        Method removes all cursors.
        """

        self.detach()
        self._cursors.clear()
        self._current_index = None

    def remove_current_cursor(self) -> None:
        """
        Method removes current cursor.
        """

        if self._current_index is not None:
            self._cursors[self._current_index].detach()
            self._cursors.pop(self._current_index)
            self._current_index = None

    def set_axis_labels(self, x_label: str, y_label: str) -> None:
        """
        :param x_label: label fot horizontal axis;
        :param y_label: label for vertical axis.
        """

        if x_label:
            self._x_label = x_label
        if y_label:
            self._y_label = y_label
        _ = [cursor.set_axis_labels(self._x_label, self._y_label) for cursor in self._cursors]

    def set_current_cursor(self, pos: QPoint) -> None:
        """
        :param pos: position where the cursor should be made current.
        """

        self._current_index = self.find_cursor_at_point(pos)
        self.paint_current_cursor()
