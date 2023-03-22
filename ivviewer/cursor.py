from typing import List, Optional, Union
import numpy as np
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from qwt import QwtPlot, QwtPlotCurve, QwtPlotMarker, QwtText
from ivviewer.curve import Point


class IvcCursor:
    """
    This class is cursor with horizontal and vertical lines, it shows coordinates for selected point.
    """

    CROSS_SIZE: int = 10  # default size of white cross in px
    DEFAULT_FONT_SIZE: int = 10
    DEFAULT_X_LABEL: str = "U"
    DEFAULT_Y_LABEL: str = "I"

    def __init__(self, pos: Point, ivc_viewer: QwtPlot, font: QFont = None, x_label: str = None, y_label: str = None,
                 accuracy: int = None) -> None:
        """
        :param pos: point at which to place cursor;
        :param ivc_viewer: plot on which to place cursor;
        :param font: font of text at cursor;
        :param x_label: name of the horizontal axis;
        :param y_label: name of the vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursor.
        """

        self._accuracy: int = accuracy
        self._font: QFont = font if isinstance(font, QFont) else QFont("", self.DEFAULT_FONT_SIZE)
        self._ivc_viewer: QwtPlot = ivc_viewer
        self._x_label: str = x_label if x_label else self.DEFAULT_X_LABEL
        self._y_label: str = y_label if y_label else self.DEFAULT_Y_LABEL

        self.x: float = None
        self.y: float = None
        self._x_axis: QwtPlotCurve = QwtPlotCurve()
        self._y_axis: QwtPlotCurve = QwtPlotCurve()

        cursor_text = QwtText()
        cursor_text.setFont(self._font)
        cursor_text.setRenderFlags(Qt.AlignLeft)
        self._marker: QwtPlotMarker = QwtPlotMarker()
        self._marker.setSpacing(10)
        self._marker.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._marker.setLabel(cursor_text)

        self._cross_x = QwtPlotCurve()
        self._cross_y = QwtPlotCurve()

        self.move(pos)

    @property
    def cursor_text(self) -> str:
        if self._accuracy is not None:
            x_value = format(self.x, f".{self._accuracy}f")
            y_value = format(self.y, f".{self._accuracy}f")
        else:
            x_value = self.x
            y_value = self.y
        return "{} = {}, {} = {}".format(self._x_label, x_value, self._y_label, y_value)

    @staticmethod
    def _get_color(param: Union[QBrush, QColor, QPen]) -> QColor:
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
        if isinstance(param, QColor):
            pen = QPen(QBrush(param), 2, Qt.DotLine)
        elif isinstance(param, QBrush):
            pen = QPen(param, 2, Qt.DotLine)
        elif isinstance(param, QPen):
            pen = param
        else:
            raise TypeError("Invalid type of argument passed. Allowed types: QBrush, QColor and QPen")
        return pen

    def _set_cross_xy(self) -> None:
        """
        Method calculates sizes and position of white cross of marker.
        """

        x = self._ivc_viewer.transform(QwtPlot.xBottom, self.x)
        x_1 = self._ivc_viewer.invTransform(QwtPlot.xBottom, x - self.CROSS_SIZE)
        x_2 = self._ivc_viewer.invTransform(QwtPlot.xBottom, x + self.CROSS_SIZE)
        y = self._ivc_viewer.transform(QwtPlot.yLeft, self.y)
        y_1 = self._ivc_viewer.invTransform(QwtPlot.yLeft, y - self.CROSS_SIZE)
        y_2 = self._ivc_viewer.invTransform(QwtPlot.yLeft, y + self.CROSS_SIZE)
        self._cross_x.setData((x_1, x_2), (self.y, self.y))
        self._cross_y.setData((self.x, self.x), (y_1, y_2))

    def attach(self, ivc_viewer: QwtPlot) -> None:
        self._ivc_viewer = ivc_viewer
        self._x_axis.attach(self._ivc_viewer)
        self._y_axis.attach(self._ivc_viewer)
        self._marker.attach(self._ivc_viewer)
        self._cross_x.attach(self._ivc_viewer)
        self._cross_y.attach(self._ivc_viewer)

    def check_point(self) -> None:
        self.x = self._marker.value().x()
        self.y = self._marker.value().y()

    def detach(self) -> None:
        self._x_axis.detach()
        self._y_axis.detach()
        self._marker.detach()
        self._cross_x.detach()
        self._cross_y.detach()

    def get_cursor_coordinates_in_px(self) -> QPoint:
        x = self._ivc_viewer.transform(QwtPlot.xBottom, self.x) + self._ivc_viewer.canvas().x()
        y = self._ivc_viewer.transform(QwtPlot.yLeft, self.y) + self._ivc_viewer.canvas().y()
        return QPoint(x, y)

    def move(self, pos: Point) -> None:
        self.x, self.y = pos.x, pos.y
        self._x_axis.setData((pos.x, pos.x), (-self._ivc_viewer.y_scale, self._ivc_viewer.y_scale))
        self._y_axis.setData((-self._ivc_viewer.x_scale, self._ivc_viewer.x_scale), (pos.y, pos.y))
        self._marker.setValue(pos.x, pos.y)
        self._marker.label().setText(self.cursor_text)
        self._set_cross_xy()

    def paint(self, param: Union[QBrush, QColor, QPen], param_for_cross: Optional[Union[QBrush, QColor, QPen]] = None
              ) -> None:
        """
        Method draws all parts of cursor with given color, brush or pen.
        :param param: brush, color or pen for cursor;
        :param param_for_cross: brush, color or pen for cross in the center of cursor.
        """

        color = self._get_color(param)
        self._marker.label().setColor(color)
        pen = self._get_pen(param)
        self._x_axis.setPen(pen)
        self._y_axis.setPen(pen)

        if not isinstance(param_for_cross, (QBrush, QColor, QPen)):
            pen_for_cross = QPen(QBrush(QColor(255, 255, 255)), 2, Qt.SolidLine)
        else:
            pen_for_cross = self._get_pen(param_for_cross)
        self._cross_x.setPen(pen_for_cross)
        self._cross_y.setPen(pen_for_cross)
        self._set_cross_xy()

    def set_axis_labels(self, x_label: str, y_label: str) -> None:
        """
        :param x_label: label for horizontal axis;
        :param y_label: label for vertical axis.
        """

        if x_label:
            self._x_label = x_label
        if y_label:
            self._y_label = y_label
        self._marker.label().setText(self.cursor_text)


class IvcCursors:
    """
    This class is array of objects of class IvcCursor.
    """

    COLOR_FOR_REST: QColor = QColor(102, 255, 0)
    COLOR_FOR_SELECTED: QColor = QColor(255, 0, 0)
    DISTANCE_FOR_SELECTION: int = 3

    def __init__(self, ivc_viewer: QwtPlot, font: QFont = None, color_for_rest: QColor = None,
                 color_for_selected: QColor = None, x_label: str = None, y_label: str = None, accuracy: int = None
                 ) -> None:
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

    @property
    def cursors(self) -> List[IvcCursor]:
        return self._cursors

    def _find_cursor_at_point(self, pos: QPoint) -> Optional[int]:

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

    def check_points(self) -> None:
        _ = [cursor.check_point() for cursor in self._cursors]

    def detach(self) -> None:
        """
        Method detaches all cursors from plot.
        """

        _ = [cursor.detach() for cursor in self._cursors]

    def find_cursor_for_context_menu(self, pos: QPoint) -> bool:
        """
        Method finds cursor at given point for context menu work.
        :param pos: point next to which you want to search for the cursor.
        :return: True if cursor at given position was found otherwise False.
        """

        cursor_index = self._find_cursor_at_point(pos)
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
        self._current_index = self._find_cursor_at_point(pos)
        self.paint_current_cursor()
