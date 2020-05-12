from typing import Optional, Tuple

import numpy as np
from collections import namedtuple

from PyQt5 import QtCore
from PyQt5.QtGui import QPen, QBrush, QColor, QFont
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtText

from .ivcviewerconstants import Voltage, Current, adjust_scale

Curve = namedtuple("Curve", ("x", "y", ))


__all__ = ["IvcViewer"]


class IvcViewer(QwtPlot):
    min_border_voltage = 1.0
    min_border_current = 0.5

    min_borders_changed = QtCore.pyqtSignal()

    reference_curve_changed = QtCore.pyqtSignal()  # Reference curve changed
    test_curve_changed = QtCore.pyqtSignal()  # Test curve changed
    curve_changed = QtCore.pyqtSignal()  # Reference or test curve changed

    def __init__(self, owner, parent=None):
        super().__init__(parent)

        self.__owner = owner
        self.__grid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        self.__grid.setMajorPen(QPen(
            QColor(0, 0, 0), 0, QtCore.Qt.SolidLine))
        self.__grid.setMinorPen(QPen(
            QColor(128, 128, 128), 0, QtCore.Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)

        # WTF?! TODO: Refactor m away!
        m = 640000  # Is said to be enough for anybody
        black_pen = QPen(QColor(0, 0, 0), 2)

        axis_font = QFont()
        axis_font.pointSize = 20
        self.setCanvasBackground(QBrush(QColor(0xe1, 0xed, 0xeb), 1))
        self.__reference_curve = None
        self.__reference_curve_plot = QwtPlotCurve()
        self.__reference_curve_plot.setPen(QPen(QColor(255, 0, 0, 200), 4))
        self.__reference_curve_plot.attach(self)

        self.__test_curve = None
        self.__test_curve_plot = QwtPlotCurve()
        self.__test_curve_plot.setPen(QPen(QColor(0, 0, 0, 200), 4))
        self.__test_curve_plot.attach(self)

        # X Axis
        x_axis = QwtPlotCurve()
        x_axis.setPen(black_pen)
        x_axis.setData((-m, m), (0, 0))
        x_axis.attach(self)
        self.setAxisFont(QwtPlot.xBottom, QFont("Consolas", 20))
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        t = QwtText(QtCore.QCoreApplication.translate("t", "\nНапряжение (В)"))
        t.setFont(axis_font)
        self.setAxisTitle(QwtPlot.xBottom, t)

        # Y Axis
        y_axis = QwtPlotCurve()
        y_axis.setPen(black_pen)
        y_axis.setData((0, 0), (-m, m))
        y_axis.attach(self)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)
        self.setAxisFont(QwtPlot.yLeft, QFont("Consolas", 20))
        t = QwtText(QtCore.QCoreApplication.translate("t", "Ток (мА)\n"))
        t.setFont(axis_font)
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

    # reference_curve management
    def get_reference_curve(self) -> Optional[Curve]:
        return self.__reference_curve

    def set_reference_curve(self, reference_curve: Optional[Curve]):
        self.__set_reference_curve(reference_curve)
        self.__adjust_scale()
        self.reference_curve_changed.emit()
        self.curve_changed.emit()

    def clear_reference_curve(self):
        self.__set_reference_curve(None)
        self.__adjust_scale()
        self.reference_curve_changed.emit()
        self.curve_changed.emit()

    # test_curve management
    def get_test_curve(self) -> Optional[Curve]:
        return self.__test_curve

    def set_test_curve(self, test_curve: Optional[Curve] = None):
        self.__set_test_curve(test_curve)
        self.__adjust_scale()
        self.test_curve_changed.emit()
        self.curve_changed.emit()

    def clear_test_curve(self):
        self.__set_test_curve(None)
        self.__adjust_scale()
        self.test_curve_changed.emit()
        self.curve_changed.emit()

    def __set_reference_curve(self, reference_curve: Optional[Curve] = None):
        self.__reference_curve = reference_curve
        _plot_curve(self.__reference_curve, self.__reference_curve_plot)

    def __set_test_curve(self, test_curve: Optional[Curve] = None):
        self.__test_curve = test_curve
        _plot_curve(self.__test_curve, self.__test_curve_plot)

    def __adjust_scale(self):
        self.setAxisScale(QwtPlot.xBottom, -self._voltage_scale, self._voltage_scale)
        self.setAxisScale(QwtPlot.yLeft, -self._current_scale, self._current_scale)

    def set_scale(self, voltage: float, current: float):
        self._voltage_scale = voltage
        self._current_scale = current
        self.__adjust_scale()

    def set_scale_const(self, voltage: Voltage, current: Current):
        self.set_scale(*adjust_scale(voltage, current))


def _plot_curve(curve: Optional[tuple], curve_plot: QwtPlotCurve) -> None:
    if curve is None or curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve[0], curve[0][0])
        currents = np.append(curve[1], curve[1][0])

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
