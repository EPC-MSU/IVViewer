import os
import platform
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QMouseEvent, QPen
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtPlotMarker, QwtText


@dataclass
class Curve:
    voltages: List[float]
    currents: List[float]


@dataclass
class Point:
    x: float
    y: float


class PlotCurve(QwtPlotCurve, QObject):
    """
    Class for curve.
    """

    DEFAULT_WIDTH: float = 4
    curve_changed: pyqtSignal = pyqtSignal()

    def __init__(self, owner: "IvcViewer", parent=None, label: Optional[str] = None) -> None:
        """
        :param owner:
        :param parent:
        :param label: label-name for curve.
        """

        QwtPlotCurve.__init__(self, parent)
        QObject.__init__(self)
        self._curve: Optional[Curve] = None
        self.parent = parent
        self.owner: "IvcViewer" = owner
        self.label: Optional[str] = label

    @property
    def curve(self) -> Optional[Curve]:
        return self._curve

    @curve.setter
    def curve(self, curve: Optional[Curve]) -> None:
        self.set_curve(curve)

    def _set_curve(self, curve: Optional[Curve] = None) -> None:
        self._curve = curve
        _plot_curve(self)

    def clear_curve(self) -> None:
        self.set_curve(None)

    def get_curve(self) -> Optional[Curve]:
        return self._curve

    def is_empty(self) -> bool:
        """
        :return: True if curve is empty.
        """

        return not self._curve

    def set_curve(self, curve: Optional[Curve]) -> None:
        self._set_curve(curve)
        self.owner._adjust_scale()
        self.curve_changed.emit()

    def set_curve_params(self, param: Union[QBrush, QColor, QPen] = QColor(0, 0, 0, 200)) -> None:
        """
        :param param: brush, color or pen for curve.
        """

        if isinstance(param, QColor):
            self.setPen(QPen(QBrush(param), self.DEFAULT_WIDTH))
        elif isinstance(param, QBrush):
            self.setPen(QPen(param, self.DEFAULT_WIDTH))
        elif isinstance(param, QPen):
            self.setPen(param)
        else:
            raise TypeError("Invalid type of argument passed. Allowed types: QBrush, QColor and QPen")


class IvcCursor:
    """
    This class is cursor with horizontal and vertical lines, it shows coordinates for selected point.
    """

    CROSS_SIZE: int = 10  # default size of white cross in px
    DEFAULT_FONT_SIZE: int = 10
    DEFAULT_X_LABEL: str = "U"
    DEFAULT_Y_LABEL: str = "I"

    def __init__(self, pos: Point, plot: "IvcViewer", font: QFont = None, x_label: str = None, y_label: str = None,
                 accuracy: int = None) -> None:
        """
        :param pos: point at which to place cursor;
        :param plot: plot on which to place cursor;
        :param font: font of text at cursor;
        :param x_label: name of the horizontal axis;
        :param y_label: name of the vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursor.
        """

        self._accuracy: int = accuracy
        self._font: QFont = font if isinstance(font, QFont) else _get_font(self.DEFAULT_FONT_SIZE)
        self._plot: "IvcViewer" = plot
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

        x = self._plot.transform(QwtPlot.xBottom, self.x)
        x_1 = self._plot.invTransform(QwtPlot.xBottom, x - self.CROSS_SIZE)
        x_2 = self._plot.invTransform(QwtPlot.xBottom, x + self.CROSS_SIZE)
        y = self._plot.transform(QwtPlot.yLeft, self.y)
        y_1 = self._plot.invTransform(QwtPlot.yLeft, y - self.CROSS_SIZE)
        y_2 = self._plot.invTransform(QwtPlot.yLeft, y + self.CROSS_SIZE)
        self._cross_x.setData((x_1, x_2), (self.y, self.y))
        self._cross_y.setData((self.x, self.x), (y_1, y_2))

    def attach(self, plot: "IvcViewer") -> None:
        self._x_axis.attach(plot)
        self._y_axis.attach(plot)
        self._marker.attach(plot)
        self._cross_x.attach(plot)
        self._cross_y.attach(plot)

    def check_point(self) -> None:
        self.x = self._marker.value().x()
        self.y = self._marker.value().y()

    def detach(self) -> None:
        self._x_axis.detach()
        self._y_axis.detach()
        self._marker.detach()
        self._cross_x.detach()
        self._cross_y.detach()

    def move(self, pos: Point) -> None:
        self.x, self.y = pos.x, pos.y
        self._x_axis.setData((pos.x, pos.x), (-self._plot.y_scale, self._plot.y_scale))
        self._y_axis.setData((-self._plot.x_scale, self._plot.x_scale), (pos.y, pos.y))
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

    K_RADIUS: float = 0.2  # coefficient of radius of action to select cursor
    COLOR_FOR_REST: QColor = QColor(102, 255, 0)
    COLOR_FOR_SELECTED: QColor = QColor(255, 0, 0)

    def __init__(self, plot: "IvcViewer", font: QFont = None, color_for_rest: QColor = None,
                 color_for_selected: QColor = None, x_label: str = None, y_label: str = None, accuracy: int = None
                 ) -> None:
        """
        :param plot: plot on which to place cursors;
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
        self._plot: "IvcViewer" = plot
        self._x_label: Optional[str] = x_label
        self._y_label: Optional[str] = y_label

    @property
    def cursors(self) -> List[IvcCursor]:
        return self._cursors

    def _find_cursor_at_point(self, pos: Point) -> Optional[int]:
        """
        Method finds cursor at given point.
        :param pos: point.
        :return: index of cursor.
        """

        width, height = self._plot.get_minor_axis_step()
        for cursor in self._cursors:
            if np.abs(cursor.x - pos.x) < self.K_RADIUS * width and np.abs(cursor.y - pos.y) < self.K_RADIUS * height:
                return self._cursors.index(cursor)
        return None

    def add_cursor(self, pos: Point) -> None:
        """
        Method adds cursor at given position.
        :param pos: position where cursor should be added.
        """

        _ = [cursor.paint(self._color_for_rest) for cursor in self._cursors]
        cursor = IvcCursor(pos, self._plot, self._font, self._x_label, self._y_label, self._accuracy)
        cursor.paint(self._color_for_selected)
        cursor.attach(self._plot)
        self._cursors.append(cursor)
        self._current_index = len(self._cursors) - 1

    def attach(self, plot: "IvcViewer") -> None:
        """
        Method attaches all cursors to plot.
        :param plot: plot.
        """

        _ = [cursor.attach(plot) for cursor in self._cursors]

    def check_points(self) -> None:
        _ = [cursor.check_point() for cursor in self._cursors]

    def detach(self) -> None:
        """
        Method detaches all cursors from plot.
        """

        _ = [cursor.detach() for cursor in self._cursors]

    def find_cursor_for_context_menu(self, pos: Point) -> bool:
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

    def set_current_cursor(self, pos: Point) -> None:
        """
        Method finds cursor at given point.
        :param pos: position near which you want to find cursor.
        """

        self._current_index = self._find_cursor_at_point(pos)
        self.paint_current_cursor()


class IvcViewer(QwtPlot):

    DEFAULT_AXIS_FONT_SIZE: int = 20
    DEFAULT_BACK_COLOR: QColor = QColor(0xe1, 0xed, 0xeb)
    DEFAULT_GRID_COLOR: QColor = QColor(0, 0, 0)
    DEFAULT_SCREENSHOT_FILE_NAME_BASE: str = "screenshot"
    DEFAULT_TEXT_COLOR: QColor = QColor(255, 0, 0)
    DEFAULT_TITLE_FONT_SIZE: int = 20
    DEFAULT_X_TITLE: str = "Напряжение, В"
    DEFAULT_X_UNIT: str = "В"
    DEFAULT_Y_TITLE: str = "Ток, мА"
    DEFAULT_Y_UNIT: str = "А"
    MIN_BORDER_Y: float = 0.5
    MIN_BORDER_X: float = 1.0
    curve_changed: pyqtSignal = pyqtSignal()
    min_borders_changed: pyqtSignal = pyqtSignal()

    def __init__(self, owner, parent=None, solid_axis_enabled: bool = True, grid_color: QColor = None,
                 back_color: QColor = None, text_color: QColor = None, color_for_rest_cursors: QColor = None,
                 color_for_selected_cursor: QColor = None, axis_label_enabled: bool = True,
                 axis_font: QFont = None, cursor_font: QFont = None, title_font: QFont = None, x_title: str = None,
                 y_title: str = None, x_label: str = None, y_label: str = None, x_unit: str = None, y_unit: str = None,
                 accuracy: int = None) -> None:
        """
        :param owner: owner widget;
        :param parent: parent widget;
        :param solid_axis_enabled: if True then axes will be shown with solid lines;
        :param grid_color: grid color;
        :param back_color: canvas background color;
        :param text_color: color of text at the center of plot;
        :param color_for_rest_cursors: color for unselected cursors;
        :param color_for_selected_cursor: color for selected cursor;
        :param axis_label_enabled: if True then labels of axes will be displayed;
        :param axis_font: font for values on axes;
        :param cursor_font: font of text at cursors;
        :param title_font: axis titles font;
        :param x_title: title for horizontal axis;
        :param y_title: title for vertical axis;
        :param x_label: short name for horizontal axis;
        :param y_label: short name for vertical axis;
        :param x_unit: unit of measure for the value along horizontal axis;
        :param y_unit: unit of measure for the value along vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursors.
        """

        super().__init__(parent)
        self._owner = owner
        self._axis_font: QFont = axis_font if isinstance(axis_font, QFont) else _get_font(self.DEFAULT_AXIS_FONT_SIZE)
        self._grid_color: QColor = grid_color if isinstance(grid_color, QColor) else self.DEFAULT_GRID_COLOR
        self._text_color: QColor = text_color if isinstance(text_color, QColor) else self.DEFAULT_TEXT_COLOR
        self._title_font: QFont = title_font if isinstance(title_font, QFont) else \
            _get_font(self.DEFAULT_TITLE_FONT_SIZE)

        self.__grid: QwtPlotGrid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        if solid_axis_enabled:
            self.__grid.setMajorPen(QPen(self._grid_color, 0, Qt.SolidLine))
        else:
            self.__grid.setMajorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        self.__grid.setMinorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)

        back_color = back_color if isinstance(back_color, QColor) else self.DEFAULT_BACK_COLOR
        self.setCanvasBackground(QBrush(back_color, Qt.SolidPattern))
        self.canvas().setCursor(QCursor(Qt.ArrowCursor))
        # Initial setup for axis scales
        self._min_border_x: float = abs(float(IvcViewer.MIN_BORDER_X))
        self._min_border_y: float = abs(float(IvcViewer.MIN_BORDER_Y))
        self._x_scale: float = None
        self._y_scale: float = None
        # X Axis
        axis_pen = QPen(QBrush(self._grid_color), 2)
        self._x_label: str = x_label
        self._x_title: str = x_title if x_title is not None else self.DEFAULT_X_TITLE
        self._x_unit: str = x_unit if x_unit is not None else self.DEFAULT_X_UNIT
        self.x_axis: QwtPlotCurve = QwtPlotCurve()
        self.x_axis.setPen(axis_pen)
        self.x_axis.attach(self)
        self.setAxisFont(QwtPlot.xBottom, self._axis_font)
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        # Y Axis
        self._y_label: str = y_label
        self._y_title: str = y_title if y_title is not None else self.DEFAULT_Y_TITLE
        self._y_unit: str = y_unit if y_unit is not None else self.DEFAULT_Y_UNIT
        self.y_axis: QwtPlotCurve = QwtPlotCurve()
        self.y_axis.setPen(axis_pen)
        self.y_axis.attach(self)
        self.setAxisFont(QwtPlot.yLeft, self._axis_font)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)

        self.enableAxis(QwtPlot.xBottom, axis_label_enabled)
        self.enableAxis(QwtPlot.yLeft, axis_label_enabled)

        self.cursors: IvcCursors = IvcCursors(self, cursor_font, color_for_rest=color_for_rest_cursors,
                                              color_for_selected=color_for_selected_cursor, x_label=x_label,
                                              y_label=y_label, accuracy=accuracy)
        self.curves: List[PlotCurve] = []
        self._center_text: QwtText = None
        self._center_text_marker: QwtPlotMarker = None
        self._lower_text = None
        self._lower_text_marker = None

        self._add_cursor_mode: bool = False
        self._remove_cursor_mode: bool = False

        self._context_menu_works_with_cursors: bool = True
        self._dir_path: str = "."
        self._screenshot_file_name_base: str = self.DEFAULT_SCREENSHOT_FILE_NAME_BASE
        self.enable_context_menu(True)

        self._items_for_localization: Dict[str, Dict[str, str]] = {
            "add_cursor": {"default": "Добавить метку"},
            "export_ivc": {"default": "Экспортировать кривые в файл"},
            "remove_all_cursors": {"default": "Удалить все метки"},
            "remove_cursor": {"default": "Удалить метку"},
            "save_screenshot": {"default": "Сохранить изображение"},
        }
        self._set_axis_titles()
        self._adjust_scale()

    @property
    def x_scale(self) -> float:
        return self._get_scale(self._x_scale, self._min_border_x)

    @property
    def y_scale(self) -> float:
        return self._get_scale(self._y_scale, self._min_border_y)

    def _adjust_scale(self) -> None:
        x_scale = self.x_scale
        y_scale = self.y_scale
        self.setAxisScale(QwtPlot.xBottom, -x_scale, x_scale)
        self.setAxisScale(QwtPlot.yLeft, -y_scale, y_scale)
        self.x_axis.setData((-self.x_scale, self.x_scale), (0, 0))
        self.y_axis.setData((0, 0), (-self.y_scale, self.y_scale))
        self._update_align_lower_text(x_scale, y_scale)

    def _get_default_path(self, file_base_name: str, extension: str) -> str:
        file_name = file_base_name + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + extension
        if not os.path.isdir(self._dir_path):
            os.makedirs(self._dir_path)
        return os.path.join(self._dir_path, file_name)

    def _get_item_label(self, item_name: str) -> str:
        item = self._items_for_localization.get(item_name, {})
        translation = item.get("translation", None)
        if translation is not None:
            return translation
        return item.get("default", "")

    @staticmethod
    def _get_scale(scale: float, min_border: float) -> float:
        if isinstance(scale, (float, int)) and abs(scale) > abs(min_border):
            return abs(scale)
        return abs(min_border)

    def _set_axis_titles(self) -> None:
        x_axis_title = QwtText(self._x_title)
        x_axis_title.setFont(self._title_font)
        self.setAxisTitle(QwtPlot.xBottom, x_axis_title)

        y_axis_title = QwtText(self._y_title)
        y_axis_title.setFont(self._title_font)
        self.setAxisTitle(QwtPlot.yLeft, y_axis_title)

        self.cursors.set_axis_labels(self._x_label, self._y_label)

    def _transform_point_coordinates(self, pos: QPoint) -> Point:
        pos_x = pos.x() - self.canvas().x()
        pos_y = pos.y() - self.canvas().y()
        x = np.round(self.invTransform(QwtPlot.xBottom, pos_x), 2)
        y = np.round(self.invTransform(QwtPlot.yLeft, pos_y), 2)
        return Point(x, y)

    def _update_align_lower_text(self, x_scale: float, y_scale: float) -> None:
        if not self._lower_text:
            return
        self._lower_text_marker.setValue(-x_scale, -y_scale)

    @pyqtSlot(QPoint)
    def add_cursor(self, position: QPoint) -> None:
        """
        Slot adds cursor and positions it at a given point.
        :param position: point where cursor should be placed.
        """

        pos = self._transform_point_coordinates(position)
        self.cursors.add_cursor(pos)
        self.cursors.check_points()

    def add_curve(self) -> PlotCurve:
        curve = PlotCurve(self)
        curve.set_curve_params(QColor(255, 0, 0, 200))
        curve.attach(self)
        curve.curve_changed.connect(self.curve_changed.emit)
        self.curves.append(curve)
        return curve

    def check_non_empty_curves(self) -> bool:
        """
        Method checks if there are non-empty curves.
        :return: True if there are non-empty curves.
        """

        return any([not curve.is_empty() for curve in self.curves])

    def clear_center_text(self) -> None:
        if self._center_text_marker:
            self._center_text_marker.detach()
            self._center_text_marker = None
            self._center_text = None
            self.__grid.attach(self)
            self.x_axis.attach(self)
            self.y_axis.attach(self)
            _ = [curve.attach(self) for curve in self.curves]
            self.cursors.attach(self)

    def clear_lower_text(self) -> None:
        if self._lower_text_marker:
            self._lower_text_marker.detach()
            self._lower_text_marker = None
            self._lower_text = None

    def clear_min_borders(self) -> None:
        self._min_border_x = abs(float(IvcViewer.MIN_BORDER_X))
        self._min_border_y = abs(float(IvcViewer.MIN_BORDER_Y))
        self._adjust_scale()
        self.min_borders_changed.emit()

    def enable_context_menu(self, enable: bool) -> None:
        """
        :param enable: if True then context menu will be enabled.
        """

        if enable:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.show_context_menu)
        else:
            self.setContextMenuPolicy(Qt.NoContextMenu)
            try:
                self.customContextMenuRequested.disconnect()
            except Exception:
                pass

    def enable_context_menu_for_cursors(self, enable: bool) -> None:
        """
        :param enable: if True then context menu can work with cursors.
        """

        self._context_menu_works_with_cursors = enable

    @pyqtSlot()
    def export_ivc(self) -> None:
        """
        Slot exports IV curves to file.
        """

        def print_to_file(file_, curve_label: str, curve_: Curve) -> None:
            print(f"\n{curve_label} curve:", file=file_)
            print(f"{self._x_unit}, {self._y_unit}", file=file_)
            for voltage, current in zip(curve_.voltages, curve_.currents):
                print(f"{voltage}, {current}", file=file_)

        default_file_name = self._get_default_path("ivc", ".csv")
        options = {}
        if platform.system().lower() != "windows":
            options["options"] = QFileDialog.DontUseNativeDialog
        file_name = QFileDialog.getSaveFileName(self, self._get_item_label("export_ivc"), default_file_name,
                                                "CSV files (*.csv)", **options)[0]
        if not file_name:
            return
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        with open(file_name, "w") as file:
            for index, curve in enumerate(self.curves, start=1):
                if curve is not None and not curve.is_empty():
                    print_to_file(file, curve.label if curve.label else index, curve.curve)

    def get_list_of_all_cursors(self) -> List[IvcCursor]:
        """
        Method returns list of all cursors.
        :return: list of all cursors.
        """

        return self.cursors.cursors

    def get_min_borders(self) -> Tuple[float, float]:
        return self._min_border_x, self._min_border_y

    def get_minor_axis_step(self) -> Tuple[float, float]:
        """
        Method returns width and height of rectangle of minor axes.
        :return: width and height.
        """

        x_map = self.__grid.xScaleDiv().ticks(self.__grid.xScaleDiv().MinorTick)
        y_map = self.__grid.yScaleDiv().ticks(self.__grid.yScaleDiv().MinorTick)
        x_step = min([round(x_map[i + 1] - x_map[i], 2) for i in range(len(x_map) - 1)])
        y_step = min([round(y_map[i + 1] - y_map[i], 2) for i in range(len(y_map) - 1)])
        return x_step, y_step

    def get_state_adding_cursor(self) -> bool:
        return self._add_cursor_mode

    def get_state_removing_cursor(self) -> bool:
        return self._remove_cursor_mode

    def localize_widget(self, **kwargs) -> None:
        for item_name, item in self._items_for_localization.items():
            item["translation"] = kwargs.get(item_name, None)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        This event handler receives mouse move events for the widget.
        :param event: mouse move event.
        """

        pos_to_move = self._transform_point_coordinates(event.pos())
        self.cursors.move_cursor(pos_to_move)

    def mousePressEvent(self, event: QMouseEvent):
        """
        This event handler receives mouse press events for the widget.
        :param event: mouse press event.
        """

        if event.button() == Qt.LeftButton and not self._center_text_marker:
            pos = self._transform_point_coordinates(event.pos())
            self.cursors.set_current_cursor(pos)
            if self._add_cursor_mode:
                self.cursors.add_cursor(pos)
            elif self._remove_cursor_mode:
                self.cursors.remove_current_cursor()
            self.cursors.check_points()
        event.accept()

    def redraw_cursors(self) -> None:
        """
        Method redraws cursors.
        """

        self.cursors.paint_current_cursor()

    @pyqtSlot()
    def remove_all_cursors(self) -> None:
        """
        Slot deletes all cursors.
        """

        self.cursors.remove_all_cursors()

    @pyqtSlot()
    def remove_cursor(self) -> None:
        """
        Slot deletes current cursor.
        """

        self.cursors.remove_current_cursor()

    @pyqtSlot()
    def save_image(self) -> None:
        """
        Slot saves graph as image.
        """

        default_file_name = self._get_default_path("image", ".png")
        options = {}
        if platform.system().lower() != "windows":
            options["options"] = QFileDialog.DontUseNativeDialog
        file_name = QFileDialog.getSaveFileName(self, self._get_item_label("save_screenshot"), default_file_name,
                                                "Images (*.png)", **options)[0]
        if not file_name:
            return
        if not file_name.endswith(".png"):
            file_name += ".png"
        self.grab().save(file_name)

    def set_center_text(self, text: str, font: QFont = None, color: QColor = None) -> None:
        """
        :param text: text to be shown in the center of the widget;
        :param font: font fot text;
        :param color: color for text.
        """

        if isinstance(self._center_text, QwtText) and self._center_text == QwtText(text):
            # Same text already here
            return
        self.clear_center_text()  # clear current text
        self.__grid.detach()
        self.x_axis.detach()
        self.y_axis.detach()
        self.cursors.detach()
        _ = [curve.detach() for curve in self.curves]

        self._center_text = QwtText(text)
        self._center_text.setFont(font if isinstance(font, QFont) else _get_font(40))
        self._center_text.setColor(color if isinstance(color, QColor) else self._text_color)
        self._center_text_marker = QwtPlotMarker()
        self._center_text_marker.setValue(0, 0)
        self._center_text_marker.setLabel(self._center_text)
        self._center_text_marker.attach(self)

    def set_lower_text(self, text: str, font: QFont = None, color: QColor = None) -> None:
        """
        :param text: text to be shown at the bottom of the widget;
        :param font: font for text;
        :param color: color for text.
        """

        if isinstance(self._lower_text, QwtText) and self._lower_text == text:
            # Same text already here
            return
        self.clear_lower_text()  # Clear current text
        self._lower_text = QwtText(text)
        self._lower_text.setFont(font if isinstance(font, QFont) else _get_font(10))
        self._lower_text.setColor(color if isinstance(color, QColor) else self._grid_color)
        self._lower_text.setRenderFlags(Qt.AlignLeft)
        self._lower_text_marker = QwtPlotMarker()
        self._lower_text_marker.setSpacing(10)
        self._lower_text_marker.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._lower_text_marker.setLabel(self._lower_text)
        self._lower_text_marker.attach(self)
        self._adjust_scale()

    def set_min_borders(self, min_x: float, min_y: float) -> None:
        self._min_border_x = abs(float(min_x))
        self._min_border_y = abs(float(min_y))
        self._adjust_scale()
        self.min_borders_changed.emit()

    def set_path_to_directory(self, dir_path: str) -> None:
        """
        Method sets path to directory where screenshots and IV curves are saved by default.
        :param dir_path: default directory path.
        """

        if os.path.isdir(dir_path):
            self._dir_path = dir_path

    def set_scale(self, x_scale: float, y_scale: float) -> None:
        self._x_scale = x_scale
        self._y_scale = y_scale
        self._adjust_scale()

    def set_state_adding_cursor(self, state: bool) -> None:
        self._add_cursor_mode = state

    def set_state_removing_cursor(self, state: bool) -> None:
        self._remove_cursor_mode = state

    def set_x_axis_title(self, title: str, label: str = None) -> None:
        """
        :param title: title for horizontal axis;
        :param label: short name for horizontal axis.
        """

        self._x_title = title
        self._x_label = label if label is not None else self._x_label
        self._set_axis_titles()

    def set_y_axis_title(self, title: str, label: str = None) -> None:
        """
        :param title: title for vertical axis;
        :param label: short name for vertical axis.
        """

        self._y_title = title
        self._y_label = label if label is not None else self._y_label
        self._set_axis_titles()

    @pyqtSlot(QPoint)
    def show_context_menu(self, pos: QPoint) -> None:
        """
        Slot shows context menu.
        :param pos: position of the context menu event that the widget receives.
        """

        if self._center_text_marker:
            return
        non_empty_curves = self.check_non_empty_curves()
        menu = QMenu(self)
        media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
        action_save_image = QAction(QIcon(os.path.join(media_dir, "save_image.png")),
                                    self._get_item_label("save_screenshot"), menu)
        action_save_image.setEnabled(non_empty_curves)
        action_save_image.triggered.connect(self.save_image)
        menu.addAction(action_save_image)
        action_export_ivc = QAction(QIcon(os.path.join(media_dir, "export.png")), self._get_item_label("export_ivc"),
                                    menu)
        action_export_ivc.setEnabled(non_empty_curves)
        action_export_ivc.triggered.connect(self.export_ivc)
        menu.addAction(action_export_ivc)
        if self._context_menu_works_with_cursors:
            action_add_cursor = QAction(QIcon(os.path.join(media_dir, "add_cursor.png")),
                                        self._get_item_label("add_cursor"), menu)
            action_add_cursor.triggered.connect(partial(self.add_cursor, pos))
            menu.addAction(action_add_cursor)
            if not self.cursors.is_empty():
                if self.cursors.find_cursor_for_context_menu(self._transform_point_coordinates(pos)):
                    action_remove_cursor = QAction(QIcon(os.path.join(media_dir, "remove_cursor.png")),
                                                   self._get_item_label("remove_cursor"), menu)
                    action_remove_cursor.triggered.connect(self.remove_cursor)
                    menu.addAction(action_remove_cursor)
                action_remove_all_cursors = QAction(QIcon(os.path.join(media_dir, "remove_all_cursors.png")),
                                                    self._get_item_label("remove_all_cursors"), menu)
                action_remove_all_cursors.triggered.connect(self.remove_all_cursors)
                menu.addAction(action_remove_all_cursors)
        menu.popup(self.mapToGlobal(pos))


def _get_font(size: int) -> QFont:
    """
    :param size: size of font.
    :return: font with given size.
    """

    font = QFont()
    font.setPointSize(size)
    return font


def _plot_curve(curve_plot: PlotCurve) -> None:
    if curve_plot.curve is None or curve_plot.curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve_plot.curve.voltages, curve_plot.curve.voltages[0])
        currents = np.append(curve_plot.curve.currents, curve_plot.curve.currents[0]) * 1000

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
