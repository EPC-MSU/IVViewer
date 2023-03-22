from typing import List, Optional, Union
from dataclasses import dataclass
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QBrush, QColor, QPen
from qwt import QwtPlot, QwtPlotCurve


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

    def __init__(self, ivc_viewer: QwtPlot, parent=None, label: Optional[str] = None) -> None:
        """
        :param ivc_viewer: plot on which to place curve;
        :param parent:
        :param label: name for curve.
        """

        QwtPlotCurve.__init__(self, parent)
        QObject.__init__(self)
        self._curve: Optional[Curve] = None
        self._ivc_viewer: QwtPlot = ivc_viewer
        self._parent = parent
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
        self._ivc_viewer._adjust_scale()
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


def _plot_curve(curve_plot: PlotCurve) -> None:
    if curve_plot.curve is None or curve_plot.curve == (None, None):
        curve_plot.setData((), ())
    else:
        # Get curves and close the loop
        voltages = np.append(curve_plot.curve.voltages, curve_plot.curve.voltages[0])
        currents = np.append(curve_plot.curve.currents, curve_plot.curve.currents[0]) * 1000

        # Setting curve data: (voltage [V], current [mA])
        curve_plot.setData(voltages, currents)
