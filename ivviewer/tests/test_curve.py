from PyQt5.QtGui import QColor, QBrush, QPen
from ivviewer import Curve, Viewer
from .utils import prepare_test


class TestCurve:

    @prepare_test
    def test_1_set_curve_param(self, window: Viewer) -> None:
        """
        Test checks curve parameters setting.
        :param window: viewer widget.
        """

        window.plot.set_scale(6.0, 6.0)

        x_1 = [-2.5, 2.5]
        y_1 = [-0.005, 0.005]
        curve_1 = window.plot.add_curve()
        curve_1.set_curve(Curve(x_1, y_1))
        color_for_curve_1 = QColor(255, 153, 102)
        curve_1.set_curve_params(color_for_curve_1)
        assert curve_1.curve.voltages == x_1
        assert curve_1.curve.currents == y_1
        assert curve_1.pen().color() == color_for_curve_1

        x_2 = [-2.5, 2.5]
        y_2 = [-0.003, 0.003]
        curve_2 = window.plot.add_curve()
        curve_2.set_curve(Curve(x_2, y_2))
        pen_for_curve_2 = QPen(QBrush(QColor(0, 153, 255)), 2)
        curve_2.set_curve_params(pen_for_curve_2)
        assert curve_2.curve.voltages == x_2
        assert curve_2.curve.currents == y_2
        assert curve_2.pen() == pen_for_curve_2

        window.setToolTip("Должно быть две прямые разных цветов и толщин")
        assert len(window.plot.curves) == 2

    @prepare_test
    def test_2_clear_curve(self, window: Viewer) -> None:
        """
        Test checks the clearing of the curve.
        :param window: viewer widget.
        """

        window.plot.set_scale(6.0, 6.0)

        x_1 = [-2.5, 0, 2.5]
        y_1 = [-0.005, 0, 0.005]
        curve_1 = window.plot.add_curve()
        curve_1.set_curve(Curve(x_1, y_1))
        curve_1.set_curve_params(QColor(255, 153, 102))

        x_2 = [-2.5, 0, 2.5]
        y_2 = [-0.003, 0, 0.003]
        curve_2 = window.plot.add_curve()
        curve_2.set_curve(Curve(x_2, y_2))
        pen_for_curve_2 = QPen(QBrush(QColor(0, 153, 255)), 2)
        curve_2.set_curve_params(pen_for_curve_2)

        curve_1.clear_curve()
        assert curve_1.curve is None
        assert curve_2.curve.voltages == x_2
        assert curve_2.curve.currents == y_2
        assert curve_2.pen() == pen_for_curve_2

        window.setToolTip("Должна быть одна прямая")
