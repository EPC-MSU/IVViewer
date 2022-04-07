import os
import platform
from datetime import datetime
from functools import partial
from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication as qApp, QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QMouseEvent, QPen
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtPlotMarker, QwtText

__all__ = ["Curve", "DEFAULT_AXIS_FONT", "DEFAULT_MARKER_FONT", "DEFAULT_TITLE_FONT", "IvcViewer"]
M = 10000
DEFAULT_AXIS_FONT: QFont = QFont("Consolas", 20)
DEFAULT_MARKER_FONT: QFont = QFont("Consolas", 10)
DEFAULT_SCREENSHOT_FILE_NAME_BASE: str = "screenshot"
DEFAULT_TITLE_FONT: QFont = QFont("Consolas", 20)


@dataclass
class Curve:
    voltages: List[float]
    currents: List[float]


@dataclass
class Point:
    x: float
    y: float


class PlotCurve(QwtPlotCurve):
    """
    Class for curve.
    """

    def __init__(self, owner: "IvcViewer", parent=None):
        super().__init__(parent)
        self.curve = None
        self.parent = parent
        self.owner: "IvcViewer" = owner

    def __set_curve(self, curve: Optional[Curve] = None):
        self.curve = curve
        _plot_curve(self)

    def clear_curve(self):
        self.__set_curve(None)
        self.owner._IvcViewer__adjust_scale()

    def get_curve(self) -> Optional[Curve]:
        return self.curve

    def set_curve(self, curve: Optional[Curve]):
        self.__set_curve(curve)
        self.owner._IvcViewer__adjust_scale()

    def set_curve_params(self, color: QColor = QColor(0, 0, 0, 200)):
        self.setPen(QPen(color, 4))


class IvcCursor:
    """
    This class is marker with x, y - axes, it shows coordinates for selected point.
    """

    CROSS_SIZE: int = 10  # default size of white cross in px

    def __init__(self, pos: Point, plot: "IvcViewer", font: QFont = DEFAULT_MARKER_FONT):
        """
        :param pos: point at which to place cursor;
        :param plot: plot on which to place cursor;
        :param font: font of text at cursor.
        """

        self.plot: "IvcViewer" = plot
        self.x: float = pos.x
        self.y: float = pos.y
        self._x_axis: QwtPlotCurve = QwtPlotCurve()
        self._y_axis: QwtPlotCurve = QwtPlotCurve()
        self._x_axis.setData((pos.x, pos.x), (-M, M))
        self._y_axis.setData((-M, M), (pos.y, pos.y))
        self.font: QFont = font
        cursor_text = QwtText("U = {}, I = {}".format(pos.x, pos.y))
        cursor_text.setFont(self.font)
        cursor_text.setRenderFlags(Qt.AlignLeft)
        self._sign: QwtPlotMarker = QwtPlotMarker()
        self._sign.setValue(pos.x, pos.y)
        self._sign.setSpacing(10)
        self._sign.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._sign.setLabel(cursor_text)
        self._cross_x = QwtPlotCurve()
        self._cross_y = QwtPlotCurve()

    def _set_cross_xy(self):
        """
        Method calculates sizes and position of white cross of marker.
        """

        x = self.plot.canvasMap(QwtPlot.xBottom).transform(self.x)
        x_1 = self.plot.canvasMap(QwtPlot.xBottom).invTransform(x - self.CROSS_SIZE)
        x_2 = self.plot.canvasMap(QwtPlot.xBottom).invTransform(x + self.CROSS_SIZE)
        y = self.plot.canvasMap(QwtPlot.yLeft).transform(self.y)
        y_1 = self.plot.canvasMap(QwtPlot.yLeft).invTransform(y - self.CROSS_SIZE)
        y_2 = self.plot.canvasMap(QwtPlot.yLeft).invTransform(y + self.CROSS_SIZE)
        self._cross_x.setData((x_1, x_2), (self.y, self.y))
        self._cross_y.setData((self.x, self.x), (y_1, y_2))

    def attach(self, plot: "IvcViewer"):
        self._x_axis.attach(plot)
        self._y_axis.attach(plot)
        self._sign.attach(plot)
        self._cross_x.attach(plot)
        self._cross_y.attach(plot)

    def check_point(self):
        self.x = self._sign.value().x()
        self.y = self._sign.value().y()

    def detach(self):
        self._x_axis.detach()
        self._y_axis.detach()
        self._sign.detach()
        self._cross_x.detach()
        self._cross_y.detach()

    def move(self, pos: Point):
        self.x, self.y = pos.x, pos.y
        self._x_axis.setData((pos.x, pos.x), (-M, M))
        self._y_axis.setData((-M, M), (pos.y, pos.y))
        self._sign.setValue(pos.x, pos.y)
        self._sign.label().setText("U = {}, I = {}".format(pos.x, pos.y))
        self._set_cross_xy()

    def paint(self, color: QColor):
        """
        Method draws all parts of marker.
        :param color: color for horizontal and vertical lines.
        """

        self._sign.label().setColor(color)
        pen = QPen(color, 2, Qt.DotLine)
        self._x_axis.setPen(pen)
        self._y_axis.setPen(pen)
        pen = QPen(QColor(255, 255, 255), 2, Qt.SolidLine)
        self._set_cross_xy()
        self._cross_x.setPen(pen)
        self._cross_y.setPen(pen)


class IvcCursors:
    """
    This class is array of objects of class IvcCursor.
    """

    K_RADIUS: float = 0.2  # coefficient of radius of action for select cursor

    def __init__(self, plot: "IvcViewer", font: QFont = DEFAULT_MARKER_FONT,
                 color_for_rest: QColor = QColor(102, 255, 0), color_for_selected: QColor = QColor(255, 0, 0)):
        """
        :param plot: plot on which to place cursors;
        :param font: font of text at cursors;
        :param color_for_rest: color for unselected cursors;
        :param color_for_selected: color for selected cursor.
        """

        self.color_for_rest: QColor = color_for_rest
        self.color_for_selected: QColor = color_for_selected
        self.current_index: int = None
        self.cursors: List[IvcCursor] = []
        self.font: QFont = font
        self.plot: "IvcViewer" = plot

    def _find_cursor_at_point(self, pos: Point) -> Optional[int]:
        """
        Method finds cursor at given point.
        :param pos: position where cursor is located.
        :return: cursor index.
        """

        width, height = self.plot.get_minor_axis_step()
        for cursor in self.cursors:
            if np.abs(cursor.x - pos.x) < self.K_RADIUS * width and np.abs(cursor.y - pos.y) < self.K_RADIUS * height:
                return self.cursors.index(cursor)
        return None

    def add_cursor(self, pos: Point):
        """
        Method adds cursor at given position.
        :param pos: position where cursor should be added.
        """

        for cursor in self.cursors:
            cursor.paint(self.color_for_rest)
        self.cursors.append(IvcCursor(pos, self.plot, self.font))
        self.cursors[-1].paint(self.color_for_selected)
        self.cursors[-1].attach(self.plot)
        self.current_index = len(self.cursors) - 1

    def attach(self, plot: "IvcViewer"):
        """
        Method attaches all cursors to plot.
        :param plot: plot.
        """

        for cursor in self.cursors:
            cursor.attach(plot)

    def check_points(self):
        for cursor in self.cursors:
            cursor.check_point()

    def detach(self):
        """
        Method detaches all cursors from plot.
        """

        for cursor in self.cursors:
            cursor.detach()

    def detach_current_cursor(self):
        """
        Method detaches current cursor from plot.
        """

        if self.current_index is not None:
            self.cursors[self.current_index].detach()

    def find_cursor_for_context_menu(self, pos: Point) -> bool:
        """
        Method finds cursor at given point for context menu work.
        :param pos: position where cursor is located.
        :return: True if cursor at given position was found otherwise False.
        """

        cursor_index = self._find_cursor_at_point(pos)
        if cursor_index is not None:
            self.current_index = cursor_index
            self.paint_current_cursor()
            return True
        return False

    def get_list_of_all_cursors(self) -> List[IvcCursor]:
        """
        Method returns list with all cursors.
        :return: list with all cursors.
        """

        return self.cursors

    def is_empty(self) -> bool:
        """
        Method checks if there are cursors.
        :return: True if object has no cursors otherwise False.
        """

        return not bool(self.cursors)

    def move_cursor(self, end_pos: Point):
        if self.current_index is not None:
            self.cursors[self.current_index].move(end_pos)

    def paint_current_cursor(self):
        for cursor in self.cursors:
            cursor.paint(self.color_for_rest)
        if self.current_index is not None:
            self.cursors[self.current_index].paint(self.color_for_selected)

    def remove_all_cursors(self):
        """
        Method removes all cursors.
        """

        self.detach()
        self.cursors.clear()
        self.current_index = None

    def remove_current_cursor(self):
        """
        Method removes current cursor.
        """

        self.detach_current_cursor()
        self.cursors.pop(self.current_index)
        self.current_index = None

    def set_current_mark(self, pos: Point):
        """
        Method finds cursor at given point.
        :param pos: position where cursor is located.
        """

        cursor_index = self._find_cursor_at_point(pos)
        if cursor_index is not None:
            self.current_index = cursor_index
        self.paint_current_cursor()


class IvcViewer(QwtPlot):

    min_border_current: float = 0.5
    min_border_voltage: float = 1.0
    min_borders_changed: pyqtSignal = pyqtSignal()

    def __init__(self, owner, parent=None, solid_axis_enabled: bool = True,
                 grid_color: QColor = QColor(0, 0, 0), back_color: QColor = QColor(0xe1, 0xed, 0xeb),
                 text_color: QColor = QColor(255, 0, 0), color_for_rest_markers: QColor = QColor(102, 255, 0),
                 color_for_selected_marker: QColor = QColor(255, 0, 0), axis_sign_enabled: bool = True,
                 axis_font: QFont = DEFAULT_AXIS_FONT, marker_font: QFont = DEFAULT_MARKER_FONT,
                 title_font: QFont = DEFAULT_TITLE_FONT,
                 screenshot_file_name_base: str = DEFAULT_SCREENSHOT_FILE_NAME_BASE):
        """
        :param owner: owner widget;
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

        super().__init__(parent)
        self.__owner = owner
        self.__grid: QwtPlotGrid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        if solid_axis_enabled:
            self.__grid.setMajorPen(QPen(grid_color, 0, Qt.SolidLine))
        else:
            self.__grid.setMajorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        self.__grid.setMinorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)
        self.text_color: QColor = text_color
        self.grid_color: QColor = grid_color

        self.setCanvasBackground(QBrush(back_color, Qt.SolidPattern))
        self.canvas().setCursor(QCursor(Qt.ArrowCursor))
        # X Axis
        axis_pen = QPen(self.grid_color, 2)
        self.x_axis: QwtPlotCurve = QwtPlotCurve()
        self.x_axis.setPen(axis_pen)
        self.x_axis.setData((-M, M), (0, 0))
        self.x_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        # Y Axis
        self.y_axis: QwtPlotCurve = QwtPlotCurve()
        self.y_axis.setPen(axis_pen)
        self.y_axis.setData((0, 0), (-M, M))
        self.y_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)
        self.axis_font: QFont = axis_font
        self.title_font: QFont = title_font
        t_x = QwtText(qApp.translate("t", "\nНапряжение (В)"))
        t_x.setFont(self.title_font)
        self.setAxisFont(QwtPlot.xBottom, self.axis_font)
        self.setAxisTitle(QwtPlot.xBottom, t_x)
        t_y = QwtText(qApp.translate("t", "Ток (мА)\n"))
        t_y.setFont(self.title_font)
        self.setAxisFont(QwtPlot.yLeft, self.axis_font)
        self.setAxisTitle(QwtPlot.yLeft, t_y)
        if not axis_sign_enabled:
            self.enableAxis(QwtPlot.xBottom, False)
            self.enableAxis(QwtPlot.yLeft, False)

        # Initial setup for axis scales
        self.__min_border_voltage: float = abs(float(IvcViewer.min_border_voltage))
        self.__min_border_current: float = abs(float(IvcViewer.min_border_current))
        self.setAxisScale(QwtPlot.xBottom, -self.__min_border_voltage, self.__min_border_voltage)
        self.setAxisScale(QwtPlot.yLeft, -self.__min_border_current, self.__min_border_current)
        self._current_scale: float = 0.4
        self._voltage_scale: float = 1.5
        self.cursors: IvcCursors = IvcCursors(self, marker_font, color_for_rest=color_for_rest_markers,
                                              color_for_selected=color_for_selected_marker)
        self.curves: List[PlotCurve] = []
        self._start_pos = None
        self._center_text: QwtText = None
        self._center_text_marker: QwtPlotMarker = None
        self._lower_text = None
        self._lower_text_marker = None
        self._add_cursor_mode: bool = False
        self._remove_cursor_mode: bool = False

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self._context_menu_works_with_markers: bool = True
        self._screenshot_dir_constant: bool = False
        self._screenshot_dir_path: str = "."
        self._screenshot_file_name_base: str = screenshot_file_name_base

    def __adjust_scale(self):
        self.setAxisScale(QwtPlot.xBottom, -self._voltage_scale, self._voltage_scale)
        self.setAxisScale(QwtPlot.yLeft, -self._current_scale, self._current_scale)
        self.__update_align_lower_text()

    def __update_align_lower_text(self):
        if not self._lower_text:
            return
        self._lower_text_marker.setValue(-self._voltage_scale, -self._current_scale)

    def _transform_point_coordinates(self, position: QPoint) -> Point:
        x = np.round(self.canvasMap(2).invTransform(position.x()), 2)
        y = np.round(self.canvasMap(0).invTransform(position.y()), 2)
        return Point(x, y)

    @pyqtSlot(QPoint)
    def add_cursor(self, position: QPoint):
        """
        Slot adds cursor and positions it at a given point.
        :param position: point where cursor should be placed.
        """

        self._start_pos = self._transform_point_coordinates(position)
        self.cursors.set_current_mark(self._start_pos)
        self.cursors.add_cursor(self._start_pos)
        self.cursors.check_points()

    def add_curve(self) -> PlotCurve:
        self.curves.append(PlotCurve(self))
        self.curves[-1].setPen(QPen(QColor(255, 0, 0, 200), 4))
        self.curves[-1].attach(self)
        return self.curves[-1]

    def clear_center_text(self):
        if self._center_text_marker:
            self._center_text_marker.detach()
            self._center_text_marker = None
            self._center_text = None
            self.cursors.attach(self)
            self.y_axis.attach(self)
            self.x_axis.attach(self)
            self.__grid.attach(self)
            for curve in self.curves:
                curve.attach(self)

    def clear_lower_text(self):
        if self._lower_text_marker:
            self._lower_text_marker.detach()
            self._lower_text_marker = None
            self._lower_text = None

    def clear_min_borders(self):
        self.__min_border_voltage = abs(float(IvcViewer.min_border_voltage))
        self.__min_border_current = abs(float(IvcViewer.min_border_current))
        self.__adjust_scale()
        self.min_borders_changed.emit()

    def enable_context_menu_for_markers(self, enable: bool):
        """
        Method enables or disables context menu to work with markers.
        :param enable: if True then context menu can work with markers.
        """

        self._context_menu_works_with_markers = enable

    def get_list_of_all_cursors(self) -> List[IvcCursor]:
        """
        Method returns list of all cursors.
        :return: list of all cursors.
        """

        return self.cursors.get_list_of_all_cursors()

    def get_min_borders(self) -> Tuple[float, float]:
        return self.__min_border_voltage, self.__min_border_current

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

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        This event handler receives mouse move events for the widget.
        :param event: mouse move event.
        """

        _end_pos = self._transform_point_coordinates(event.pos())
        self.cursors.move_cursor(_end_pos)

    def mousePressEvent(self, event: QMouseEvent):
        """
        This event handler receives mouse press events for the widget.
        :param event: mouse press event.
        """

        self._start_pos = self._transform_point_coordinates(event.pos())
        self.cursors.set_current_mark(self._start_pos)
        if event.button() == Qt.LeftButton and not self._center_text_marker:
            if self._add_cursor_mode:
                self.cursors.add_cursor(self._start_pos)
                event.accept()
            elif self._remove_cursor_mode:
                self.cursors.detach_current_cursor()
                event.accept()
            self.cursors.check_points()

    def redraw_cursors(self):
        """
        Method redraws cursors.
        """

        self.cursors.paint_current_cursor()

    @pyqtSlot()
    def remove_all_cursors(self):
        """
        Slot deletes all cursors.
        """

        self.cursors.remove_all_cursors()

    @pyqtSlot()
    def remove_cursor(self):
        """
        Slot deletes current cursor.
        """

        self.cursors.remove_current_cursor()

    @pyqtSlot()
    def save_image(self):
        """
        Slot saves graph as image.
        """

        file_name = self._screenshot_file_name_base + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        if not os.path.isdir(self._screenshot_dir_path):
            os.makedirs(self._screenshot_dir_path)
        default_file_name = os.path.join(self._screenshot_dir_path, file_name)
        if platform.system().lower() == "windows":
            file_name = QFileDialog.getSaveFileName(self, qApp.translate("t", "Сохранить изображение"),
                                                    default_file_name, "Images (*.png)")[0]
        else:
            file_name = QFileDialog.getSaveFileName(self, qApp.translate("t", "Сохранить изображение"),
                                                    default_file_name, "Images (*.png)",
                                                    options=QFileDialog.DontUseNativeDialog)[0]
        if file_name:
            if not self._screenshot_dir_constant:
                self._screenshot_dir_path = os.path.dirname(file_name)
            self.grab().save(file_name)

    def set_center_text(self, text: str):
        if isinstance(self._center_text, QwtText) and self._center_text == QwtText(text):
            # Same text already here
            return
        self.clear_center_text()  # clear current text
        self.y_axis.detach()
        self.x_axis.detach()
        self.__grid.detach()
        self.cursors.detach()
        for curve in self.curves:
            curve.detach()
        font = QFont()
        font.setPointSize(40)
        self._center_text = QwtText(text)
        self._center_text.setFont(font)
        self._center_text.setColor(self.text_color)
        self._center_text_marker = QwtPlotMarker()
        self._center_text_marker.setValue(0, 0)
        self._center_text_marker.setLabel(self._center_text)
        self._center_text_marker.attach(self)

    def set_constant_screenshot_directory(self, status: bool = True):
        """
        Method sets mode in which default directory for screenshots does not change.
        :param status: if True then default directory for screenshots will not be changed.
        """

        self._screenshot_dir_constant = status

    def set_lower_text(self, text: str):
        if isinstance(self._lower_text, QwtText) and self._lower_text == text:
            # Same text already here
            return
        self.clear_lower_text()  # Clear current text
        font = QFont()
        font.setPointSize(10)
        self._lower_text = QwtText(text)
        self._lower_text.setFont(font)
        self._lower_text.setColor(self.grid_color)
        self._lower_text.setRenderFlags(Qt.AlignLeft)
        self._lower_text_marker = QwtPlotMarker()
        self._lower_text_marker.setValue(-self._voltage_scale, -self._current_scale)
        self._lower_text_marker.setSpacing(10)
        self._lower_text_marker.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._lower_text_marker.setLabel(self._lower_text)
        self._lower_text_marker.attach(self)

    def set_min_borders(self, voltage: float, current: float):
        self.__min_border_voltage = abs(float(voltage))
        self.__min_border_current = abs(float(current))
        self.__adjust_scale()
        self.min_borders_changed.emit()

    def set_path_to_screenshot_directory(self, dir_path: str):
        """
        Method sets path to directory where screenshots are saved by default.
        :param dir_path: default directory path.
        """

        if os.path.isdir(dir_path):
            self._screenshot_dir_path = dir_path

    def set_scale(self, voltage: float, current: float):
        self._voltage_scale = voltage
        self._current_scale = current
        self.__adjust_scale()

    def set_state_adding_cursor(self, state: bool):
        self._add_cursor_mode = state

    def set_state_removing_cursor(self, state: bool):
        self._remove_cursor_mode = state

    def set_x_axis_title(self, title: str):
        """
        Method sets new title to X axis.
        :param title: new title for X axis.
        """

        self.setAxisTitle(QwtPlot.xBottom, title)

    def set_y_axis_title(self, title: str):
        """
        Method sets new title to Y axis.
        :param title: new title for Y axis.
        """

        self.setAxisTitle(QwtPlot.yLeft, title)

    @pyqtSlot(QPoint)
    def show_context_menu(self, position: QPoint):
        """
        Slot shows context menu.
        :param position: position of the context menu event that the widget receives.
        """

        if self._center_text_marker:
            return
        menu = QMenu(self)
        dir_name = os.path.dirname(os.path.abspath(__file__))
        icon = QIcon(os.path.join(dir_name, "media", "save_image.png"))
        action_save_image = QAction(icon, qApp.translate("t", "Сохранить график как изображение"), menu)
        action_save_image.triggered.connect(self.save_image)
        menu.addAction(action_save_image)
        if self._context_menu_works_with_markers:
            pos_for_marker = position - QPoint(self.canvas().x(), 0)
            icon = QIcon(os.path.join(dir_name, "media", "add_cursor.png"))
            action_add_cursor = QAction(icon, qApp.translate("t", "Добавить метку"), menu)
            action_add_cursor.triggered.connect(partial(self.add_cursor, pos_for_marker))
            menu.addAction(action_add_cursor)
            if not self.cursors.is_empty():
                pos = self._transform_point_coordinates(pos_for_marker)
                if self.cursors.find_cursor_for_context_menu(pos):
                    icon = QIcon(os.path.join(dir_name, "media", "delete_cursor.png"))
                    action_remove_cursor = QAction(icon, qApp.translate("t", "Удалить метку"), menu)
                    action_remove_cursor.triggered.connect(self.remove_cursor)
                    menu.addAction(action_remove_cursor)
                icon = QIcon(os.path.join(dir_name, "media", "delete_all.png"))
                action_remove_all_cursors = QAction(icon, qApp.translate("t", "Удалить все метки"), menu)
                action_remove_all_cursors.triggered.connect(self.remove_all_cursors)
                menu.addAction(action_remove_all_cursors)
        menu.popup(self.mapToGlobal(position))

    def show_rect_axes(self):
        """
        Method shows plot in rectangle each side of which is an axis.
        """

        for axis in (QwtPlot.xBottom, QwtPlot.xTop, QwtPlot.yLeft, QwtPlot.yRight):
            self.enableAxis(axis, True)
            self.setAxisMaxMajor(axis, 5)
            self.setAxisMaxMinor(axis, 5)
        self.setAxisFont(QwtPlot.xTop, self.axis_font)
        self.setAxisFont(QwtPlot.yRight, self.axis_font)
        self.setAxisScale(QwtPlot.xTop, -self._voltage_scale, self._voltage_scale)
        self.setAxisScale(QwtPlot.yRight, -self._current_scale, self._current_scale)


def _plot_curve(curve_plot: PlotCurve):
    if curve_plot.curve is None or curve_plot.curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve_plot.curve.voltages, curve_plot.curve.voltages[0])
        currents = np.append(curve_plot.curve.currents, curve_plot.curve.currents[0]) * 1000

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
