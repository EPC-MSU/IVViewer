from typing import Optional, Tuple

import numpy as np
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtGui import QPen, QBrush, QColor, QFont
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


class IvcViewer(QwtPlot):
    min_border_voltage = 1.0
    min_border_current = 0.5
    curves = []

    min_borders_changed = QtCore.pyqtSignal()

    def __init__(self, owner, parent=None, grid_color=QColor(0, 0, 0), back_color=QColor(0xe1, 0xed, 0xeb),
                 text_color=QColor(255, 0, 0), axis_sign_enabled=True):
        super().__init__(parent)

        self.__owner = owner
        self.__grid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        self.__grid.setMajorPen(QPen(
            grid_color, 0, QtCore.Qt.SolidLine))
        self.__grid.setMinorPen(QPen(
            QColor(128, 128, 128), 0, QtCore.Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)
        self.text_color = text_color
        # WTF?! TODO: Refactor m away!
        m = 640000  # Is said to be enough for anybody
        black_pen = QPen(grid_color, 2)

        axis_font = QFont()
        axis_font.pointSize = 20
        self.setCanvasBackground(QBrush(back_color, 1))

        # X Axis
        self.x_axis = QwtPlotCurve()
        self.x_axis.setPen(black_pen)
        self.x_axis.setData((-m, m), (0, 0))
        self.x_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        t = QwtText(QtCore.QCoreApplication.translate("t", "\nНапряжение (В)"))
        t.setFont(axis_font)
        if axis_sign_enabled:
            self.setAxisFont(QwtPlot.xBottom, QFont("Consolas", 20))
            self.setAxisTitle(QwtPlot.xBottom, t)

        # Y Axis
        self.y_axis = QwtPlotCurve()
        self.y_axis.setPen(black_pen)
        self.y_axis.setData((0, 0), (-m, m))
        self.y_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)
        t = QwtText(QtCore.QCoreApplication.translate("t", "Ток (мА)\n"))
        t.setFont(axis_font)
        if axis_sign_enabled:
            self.setAxisFont(QwtPlot.yLeft, QFont("Consolas", 20))
            self.setAxisTitle(QwtPlot.yLeft, t)

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

        self._text_marker = None
        self._text = None

    def set_center_text(self, text: str):
        if self._text == text:
            return  # Same text already here

        self.clear_text()  # Clear current text
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
        self._text_marker = marker
        self._text = text

    def clear_text(self):
        if self._text_marker:
            self._text_marker.detach()
            self._text = None

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
