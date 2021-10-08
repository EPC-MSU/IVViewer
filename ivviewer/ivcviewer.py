import os
from dataclasses import dataclass
from functools import partial
from typing import List, Optional, Tuple
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication as qApp, QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QFont, QPen
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtPlotMarker, QwtText

__all__ = ["IvcViewer"]
m = 10000


@dataclass
class Curve:
    voltages: List[float]
    currents: List[float]


@dataclass
class Point:
    x: float
    y: float


class PlotCurve(QwtPlotCurve):

    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.curve = None
        self.parent = parent
        self.owner = owner

    def get_curve(self) -> Optional[Curve]:
        return self.curve

    def set_curve(self, curve: Optional[Curve]):
        self.__set_curve(curve)
        self.owner._IvcViewer__adjust_scale()

    def clear_curve(self):
        self.__set_curve(None)
        self.owner._IvcViewer__adjust_scale()

    def set_curve_params(self, color: QColor = QColor(0, 0, 0, 200)):
        self.setPen(QPen(color, 4))

    def __set_curve(self, curve: Optional[Curve] = None):
        self.curve = curve
        _plot_curve(self)


class IvcCursor:
    """
    This class is marker with x, y - axes, it shows coordinates for select
    point.
    """

    CROSS_SIZE = 10  # default size of white cross in px

    def __init__(self, pos: Point, plot):
        self.plot = plot
        self._x_axis = QwtPlotCurve()
        self._y_axis = QwtPlotCurve()
        self._sign = QwtPlotMarker()
        self._cross = QwtPlotMarker()
        self.x = pos.x
        self.y = pos.y
        self._x_axis.setData((pos.x, pos.x), (-m, m))
        self._y_axis.setData((-m, m), (pos.y, pos.y))
        tt = QwtText("U = {}, I = {}".format(pos.x, pos.y))
        tt.setFont(QFont())
        tt.font().setPointSize(10)
        tt.setRenderFlags(Qt.AlignLeft)
        self._sign.setValue(pos.x, pos.y)
        self._sign.setSpacing(10)
        self._sign.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._sign.setLabel(tt)
        self._cross_x = QwtPlotCurve()
        self._cross_y = QwtPlotCurve()

    def attach(self, plot):
        self._x_axis.attach(plot)
        self._y_axis.attach(plot)
        self._sign.attach(plot)
        self._cross_x.attach(plot)
        self._cross_y.attach(plot)

    def detach(self):
        self._x_axis.detach()
        self._y_axis.detach()
        self._sign.detach()
        self._cross_x.detach()
        self._cross_y.detach()

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

    def paint(self, color: QColor):
        """
        Method draw all parts of marker.
        :param color: color for horizontal and vertical lines.
        """

        pen = QPen(color, 2, Qt.DotLine)
        self._sign.label().setColor(color)
        self._x_axis.setPen(pen)
        self._y_axis.setPen(pen)
        pen = QPen(QColor(255, 255, 255), 2, Qt.SolidLine)
        self._set_cross_xy()
        self._cross_x.setPen(pen)
        self._cross_y.setPen(pen)

    def move(self, pos: Point):
        self.x, self.y = pos.x, pos.y
        self._x_axis.setData((pos.x, pos.x), (-m, m))
        self._y_axis.setData((-m, m), (pos.y, pos.y))
        # self._cross.setValue(pos.x, pos.y)
        self._sign.setValue(pos.x, pos.y)
        self._sign.label().setText("U = {}, I = {}".format(pos.x, pos.y))
        self._set_cross_xy()

    def check_point(self):
        self.x = self._sign.value().x()
        self.y = self._sign.value().y()


class IvcCursors:
    """
    This class is array of objects of class IvcCursor.
    """

    cursors = []
    current_color = QColor(255, 0, 0)  # color of select cursor
    last_color = QColor(102, 255, 0)  # color for rest cursors
    k_radius = 0.2  # coefficient of radius of action for select cursor

    def __init__(self, plot):
        self.plot = plot
        self.current_index = None

    def add_cursor(self, pos: Point):
        """
        Method adds cursor at given position.
        :param pos: position where cursor should be added.
        """

        for cursor in self.cursors:
            cursor.paint(self.last_color)
        self.cursors.append(IvcCursor(pos, self.plot))
        self.cursors[-1].paint(self.current_color)
        self.cursors[-1].attach(self.plot)
        self.current_index = len(self.cursors) - 1

    def attach(self, plot):
        for cursor in self.cursors:
            cursor.attach(plot)

    def check_points(self):
        for cursor in self.cursors:
            cursor.check_point()

    def del_cursor(self):
        """
        Method deletes current cursor.
        """

        if self.current_index is not None:
            self.cursors[self.current_index].detach()

    def detach(self):
        for cursor in self.cursors:
            cursor.detach()

    def is_empty(self) -> bool:
        """
        Method checks if there are cursors.
        :return: True if object has no cursors otherwise True.
        """

        return not bool(self.cursors)

    def move_cursor(self, end_pos: Point):
        if self.current_index is not None:
            self.cursors[self.current_index].move(end_pos)

    def paint_current_cursor(self):
        for cursor in self.cursors:
            cursor.paint(self.last_color)
        if self.current_index is not None:
            self.cursors[self.current_index].paint(self.current_color)

    def set_current_mark(self, pos: Point):
        """
        Method finds cursor at given point.
        :param pos: position where cursor is located.
        """

        width, height = self.plot.get_minor_axis_step()
        for cursor in self.cursors:
            if (np.abs(cursor.x - pos.x) < self.k_radius * width and
                    np.abs(cursor.y - pos.y) < self.k_radius * height):
                self.current_index = self.cursors.index(cursor)
        self.paint_current_cursor()


class IvcViewer(QwtPlot):

    min_border_voltage = 1.0
    min_border_current = 0.5
    curves = []
    min_borders_changed = pyqtSignal()

    def __init__(self, owner, parent=None, solid_axis_enabled=True, grid_color=QColor(0, 0, 0),
                 back_color=QColor(0xe1, 0xed, 0xeb), text_color=QColor(255, 0, 0),
                 axis_sign_enabled=True):
        super().__init__(parent)
        self.__owner = owner
        self.__grid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        if solid_axis_enabled:
            self.__grid.setMajorPen(QPen(grid_color, 0, Qt.SolidLine))
        else:
            self.__grid.setMajorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        self.__grid.setMinorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)
        self.text_color = text_color
        self.grid_color = grid_color

        axis_font = QFont()
        axis_font.pointSize = 20
        self.setCanvasBackground(QBrush(back_color, 1))
        self.canvas().setCursor(QCursor(Qt.ArrowCursor))
        axis_pen = QPen(self.grid_color, 2)
        # X Axis
        self.x_axis = QwtPlotCurve()
        self.x_axis.setPen(axis_pen)
        self.x_axis.setData((-m, m), (0, 0))
        self.x_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        # Y Axis
        self.y_axis = QwtPlotCurve()
        self.y_axis.setPen(axis_pen)
        self.y_axis.setData((0, 0), (-m, m))
        self.y_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)
        t_x = QwtText(qApp.translate("t", "\nНапряжение (В)"))
        t_x.setFont(axis_font)
        self.setAxisFont(QwtPlot.xBottom, QFont("Consolas", 20))
        self.setAxisTitle(QwtPlot.xBottom, t_x)
        t_y = QwtText(qApp.translate("t", "Ток (мА)\n"))
        t_y.setFont(axis_font)
        self.setAxisFont(QwtPlot.yLeft, QFont("Consolas", 20))
        self.setAxisTitle(QwtPlot.yLeft, t_y)
        if not axis_sign_enabled:
            self.enableAxis(QwtPlot.xBottom, False)
            self.enableAxis(QwtPlot.yLeft, False)

        # Initial setup for axis scales
        self.__min_border_voltage = abs(float(IvcViewer.min_border_voltage))
        self.__min_border_current = abs(float(IvcViewer.min_border_current))
        self.setAxisScale(QwtPlot.xBottom, -self.__min_border_voltage, self.__min_border_voltage)
        self.setAxisScale(QwtPlot.yLeft, -self.__min_border_current, self.__min_border_current)
        self._current_scale = 0.4
        self._voltage_scale = 1.5
        self.cursors = IvcCursors(self)
        self._start_pos = None
        self._lower_text_marker = None
        self._center_text_marker = None
        self._center_text = None
        self._lower_text = None
        self._add_cursor_mode = False
        self._remove_cursor_mode = False

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self._image_dir_path: str = "."
        self._context_menu_works_with_markers: bool = True

    @pyqtSlot(QPoint)
    def add_cursor(self, position: QPoint):
        """
        Slot adds cursor and positions it at a given point.
        :param position: point where cursor should be placed.
        """

        x = np.round(self.canvasMap(2).invTransform(position.x()), 2)
        y = np.round(self.canvasMap(0).invTransform(position.y()), 2)
        self._start_pos = Point(x, y)
        self.cursors.set_current_mark(self._start_pos)
        self.cursors.add_cursor(self._start_pos)
        self.cursors.check_points()

    def enable_context_menu_for_markers(self, enable: bool):
        """
        Method enables or disables context menu to work with markers.
        :param enable: if True then context menu can work with markers.
        """

        self._context_menu_works_with_markers = enable

    @pyqtSlot()
    def remove_all_cursors(self):
        """
        Slot deletes all cursors.
        """

        print("Удалить все курсоры")
        self.cursors.detach()
        print(self.cursors.cursors)

    @pyqtSlot()
    def save_image(self):
        """
        Slot saves graph as image.
        """

        file_name = QFileDialog.getSaveFileName(self, qApp.translate("t", "Сохранить изображение"),
                                                self._image_dir_path, "Images (*.png)")[0]
        if file_name:
            self._image_dir_path = os.path.dirname(file_name)
            self.grab().save(file_name)

    def set_path_to_default_directory(self, dir_path: str):
        """
        Method sets path to directory where images are saved by default.
        :param dir_path: default directory path.
        """

        self._image_dir_path = dir_path

    @pyqtSlot(QPoint)
    def show_context_menu(self, position: QPoint):
        """
        Slot shows context menu.
        :param position: position of the context menu event that the widget
        receives.
        """

        menu = QMenu(self)
        action_save_image = QAction(qApp.translate("t", "Сохранить график как изображение"), menu)
        action_save_image.triggered.connect(self.save_image)
        menu.addAction(action_save_image)
        if self._context_menu_works_with_markers:
            action_add_cursor = QAction(qApp.translate("t", "Добавить маркер"), menu)
            action_add_cursor.triggered.connect(partial(self.add_cursor, position))
            menu.addAction(action_add_cursor)
            if not self.cursors.is_empty():
                action_remove_all_cursors = QAction(qApp.translate("t", "Удалить все курсоры"), menu)
                action_remove_all_cursors.triggered.connect(self.remove_all_cursors)
                menu.addAction(action_remove_all_cursors)
        menu.popup(self.mapToGlobal(position))

    def set_state_adding_cursor(self, state):
        self._add_cursor_mode = state

    def set_state_removing_cursor(self, state):
        self._remove_cursor_mode = state

    def get_state_adding_cursor(self):
        return self._add_cursor_mode

    def get_state_removing_cursor(self):
        return self._remove_cursor_mode

    def mousePressEvent(self, event):
        x = np.round(self.canvasMap(2).invTransform(event.x()), 2)
        y = np.round(self.canvasMap(0).invTransform(event.y()), 2)
        self._start_pos = Point(x, y)
        self.cursors.set_current_mark(self._start_pos)
        if event.button() == Qt.LeftButton:
            if self._add_cursor_mode:
                self.cursors.add_cursor(self._start_pos)
                event.accept()
            elif self._remove_cursor_mode:
                self.cursors.del_cursor()
                event.accept()
            self.cursors.check_points()

    def mouseMoveEvent(self, event):
        x = np.round(self.canvasMap(2).invTransform(event.x()), 2)
        y = np.round(self.canvasMap(0).invTransform(event.y()), 2)
        _end_pos = Point(x, y)
        self.cursors.move_cursor(_end_pos)

    def set_center_text(self, text: str):
        if self._center_text == text:
            return  # Same text already here

        self.clear_center_text()  # Clear current text
        self.y_axis.detach()
        self.x_axis.detach()
        self.__grid.detach()
        self.cursors.detach()
        for curve in self.curves:
            curve.detach()
        tt = QwtText(text)
        font = QFont()
        font.setPointSize(40)
        tt.setFont(font)
        tt.setColor(self.text_color)
        marker = QwtPlotMarker()
        marker.setValue(0, 0)
        marker.setLabel(tt)
        marker.attach(self)
        self._center_text_marker = marker
        self._center_text = text

    def set_lower_text(self, text: str):
        if self._lower_text == text:
            return  # Same text already here

        self.clear_lower_text()  # Clear current text
        tt = QwtText(text)
        font = QFont()
        font.setPointSize(10)
        tt.setFont(font)
        tt.setColor(self.grid_color)
        tt.setRenderFlags(Qt.AlignLeft)
        marker = QwtPlotMarker()
        marker.setValue(-self._voltage_scale, -self._current_scale)
        marker.setSpacing(10)
        marker.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        marker.setLabel(tt)
        marker.attach(self)
        self._lower_text_marker = marker
        self._lower_text = text

    def clear_center_text(self):
        if self._center_text_marker:
            self._center_text_marker.detach()
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
            self._lower_text = None

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

    # min_bounds management
    def get_min_borders(self) -> Tuple[float, float]:
        return self.__min_border_voltage, self.__min_border_current

    def set_min_borders(self, voltage: float, current: float):
        self.__min_border_voltage = abs(float(voltage))
        self.__min_border_current = abs(float(current))
        self.__adjust_scale()
        self.min_borders_changed.emit()

    def clear_min_borders(self):
        self.__min_border_voltage = abs(float(IvcViewer.min_border_voltage))
        self.__min_border_current = abs(float(IvcViewer.min_border_current))
        self.__adjust_scale()
        self.min_borders_changed.emit()

    def add_curve(self) -> PlotCurve:
        self.curves.append(PlotCurve(self))
        self.curves[-1].setPen(QPen(QColor(255, 0, 0, 200), 4))
        self.curves[-1].attach(self)
        return self.curves[-1]

    def __adjust_scale(self):
        self.setAxisScale(QwtPlot.xBottom, -self._voltage_scale, self._voltage_scale)
        self.setAxisScale(QwtPlot.yLeft, -self._current_scale, self._current_scale)
        self.__update_align_lower_text()

    def __update_align_lower_text(self):
        if not self._lower_text:
            return
        self._lower_text_marker.setValue(-self._voltage_scale, -self._current_scale)

    def set_scale(self, voltage: float, current: float):
        self._voltage_scale = voltage
        self._current_scale = current
        self.__adjust_scale()

    def redraw_cursors(self):
        """
        Method redraw cursors.
        """

        self.cursors.paint_current_cursor()


def _plot_curve(curve_plot: PlotCurve) -> None:
    if curve_plot.curve is None or curve_plot.curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve_plot.curve.voltages, curve_plot.curve.voltages[0])
        currents = np.append(curve_plot.curve.currents, curve_plot.curve.currents[0]) * 1000

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
