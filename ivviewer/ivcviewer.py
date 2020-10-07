from typing import Optional, Tuple

import numpy as np
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QCursor
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtText, QwtPlotMarker

from typing import List


@dataclass
class Curve:
    voltages: List[float]
    currents: List[float]


__all__ = ["IvcViewer"]


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
    x_axis = QwtPlotCurve()
    y_axis = QwtPlotCurve()
    sign = QwtPlotMarker()
    color = QColor(255, 0, 0)

    def __init__(self, plot, x, y):
        m = 10000
        pen = QPen(self.color, 2, QtCore.Qt.DotLine)
        self.point = (x, y)
        self.x_axis.setPen(pen)
        self.x_axis.setData((x, x), (-m, m))
        self.y_axis.setPen(pen)
        self.y_axis.setData((-m, m), (y, y))
        tt = QwtText("x = {}, y = {}".format(x, y))
        font = QFont()
        font.setPointSize(8)
        tt.setFont(font)
        tt.setColor(self.color)
        tt.setRenderFlags(QtCore.Qt.AlignLeft)
        self.sign.setValue(x, y)
        self.sign.setSpacing(10)
        self.sign.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self.sign.setLabel(tt)
        self.attach(plot)

    def attach(self, plot):
        self.x_axis.attach(plot)
        self.y_axis.attach(plot)
        self.sign.attach(plot)

    def __del__(self):
        self.x_axis.detach()
        self.y_axis.detach()
        self.sign.detach()


class IvcViewer(QwtPlot):
    min_border_voltage = 1.0
    min_border_current = 0.5
    curves = []
    cursors = []

    min_borders_changed = QtCore.pyqtSignal()

    def __init__(self, owner, parent=None,
                 solid_axis_enabled=True,
                 grid_color=QColor(0, 0, 0), back_color=QColor(0xe1, 0xed, 0xeb),
                 text_color=QColor(255, 0, 0), axis_sign_enabled=True):
        super().__init__(parent)

        self.__owner = owner
        self.__grid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        if solid_axis_enabled:
            self.__grid.setMajorPen(QPen(
                grid_color, 0, QtCore.Qt.SolidLine))
        else:
            self.__grid.setMajorPen(QPen(
                QColor(128, 128, 128), 0, QtCore.Qt.DotLine))
        self.__grid.setMinorPen(QPen(
            QColor(128, 128, 128), 0, QtCore.Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)
        self.text_color = text_color
        self.grid_color = grid_color
        # WTF?! TODO: Refactor m away!
        m = 10000  # Is said to be enough for anybody

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
        t_x = QwtText(QtCore.QCoreApplication.translate("t", "\nНапряжение (В)"))
        t_x.setFont(axis_font)
        self.setAxisFont(QwtPlot.xBottom, QFont("Consolas", 20))
        self.setAxisTitle(QwtPlot.xBottom, t_x)
        t_y = QwtText(QtCore.QCoreApplication.translate("t", "Ток (мА)\n"))
        t_y.setFont(axis_font)
        self.setAxisFont(QwtPlot.yLeft, QFont("Consolas", 20))
        self.setAxisTitle(QwtPlot.yLeft, t_y)
        if not axis_sign_enabled:
            self.enableAxis(QwtPlot.xBottom, False)
            self.enableAxis(QwtPlot.yLeft, False)

        # Initial setup for axis scales
        self.__min_border_voltage = abs(float(IvcViewer.min_border_voltage))
        self.__min_border_current = abs(float(IvcViewer.min_border_current))
        self.setAxisScale(
            QwtPlot.xBottom,
            -self.__min_border_voltage,
            self.__min_border_voltage)
        self.setAxisScale(
            QwtPlot.yLeft,
            -self.__min_border_current,
            self.__min_border_current)
        self._current_scale = 0.4
        self._voltage_scale = 1.5

        self._lower_text_marker = None
        self._center_text_marker = None
        self._center_text = None
        self._lower_text = None
        self._add_cursor_mode = False
        self._remove_cursor_mode = False

    def activate_adding_cursor(self):
        self._add_cursor_mode = True

    def activate_removing_cursor(self):
        self._remove_cursor_mode = True

    def mousePressEvent(self, event):
        x = np.round(self.canvasMap(2).invTransform(event.x()), 2)
        y = np.round(self.canvasMap(0).invTransform(event.y()), 2)
        if self._add_cursor_mode:
            if event.button() == Qt.LeftButton:
                self.cursors.append(IvcCursor(self, x, y))
                self._add_cursor_mode = False
                event.accept()
        elif self._remove_cursor_mode:
            if event.button() == Qt.LeftButton:
                for cursor in self.cursors:
                    if np.abs(cursor.point[0] - x) < 0.1 and np.abs(cursor.point[1] - y) < 0.1:
                        self.cursors.remove(cursor)
                self._remove_cursor_mode = False
                event.accept()

    def set_center_text(self, text: str):
        if self._center_text == text:
            return  # Same text already here

        self.clear_center_text()  # Clear current text
        self.y_axis.detach()
        self.x_axis.detach()
        self.__grid.detach()
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
        tt.setRenderFlags(QtCore.Qt.AlignLeft)
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
            self.y_axis.attach(self)
            self.x_axis.attach(self)
            self.__grid.attach(self)
            for curve in self.curves:
                curve.attach(self)

    def clear_lower_text(self):
        if self._lower_text_marker:
            self._lower_text_marker.detach()
            self._lower_text = None

    def get_minor_axis_step(self):
        """
        Function return width and height of rectangle of minor axes
        :return: width, height
        """
        xmap = self.__grid.xScaleDiv().ticks(self.__grid.xScaleDiv().MinorTick)
        ymap = self.__grid.yScaleDiv().ticks(self.__grid.yScaleDiv().MinorTick)
        x_step = min([round(xmap[i + 1] - xmap[i], 2) for i in range(len(xmap) - 1)])
        y_step = min([round(ymap[i + 1] - ymap[i], 2) for i in range(len(ymap) - 1)])
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


def _plot_curve(curve_plot: PlotCurve) -> None:
    if curve_plot.curve is None or curve_plot.curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve_plot.curve.voltages, curve_plot.curve.voltages[0])
        currents = np.append(curve_plot.curve.currents, curve_plot.curve.currents[0]) * 1000

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
