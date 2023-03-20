import sys
import unittest
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QApplication
from ivviewer import Curve, Viewer


class TestCurve(unittest.TestCase):

    def test_1_set_curve_param(self) -> None:
        """
        Test checks curve parameters setting. Test shows viewer window with three straight lines. Each line has its own
        color and thickness.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.set_scale(6.0, 6.0)

        x_1 = [-2.5, 2.5]
        y_1 = [-0.005, 0.005]
        curve_1 = window.plot.add_curve()
        curve_1.set_curve(Curve(x_1, y_1))
        curve_1.set_curve_param(QColor(255, 153, 102))
        self.assertEqual(curve_1.curve.voltages, x_1)
        self.assertEqual(curve_1.curve.currents, y_1)

        x_2 = [-2.5, 2.5]
        y_2 = [-0.003, 0.003]
        curve_2 = window.plot.add_curve()
        curve_2.set_curve(Curve(x_2, y_2))
        curve_2.set_curve_param(QPen(QBrush(QColor(0, 153, 255)), 2))
        self.assertEqual(curve_2.curve.voltages, x_2)
        self.assertEqual(curve_2.curve.currents, y_2)

        window.setToolTip("Должно быть две прямые разных цветов и толщин")
        window.show()
        app.exec()
        self.assertEqual(len(window.plot.curves), 2)

    def test_2_clear_curve(self) -> None:
        """
        Test checks the clearing of the curve. Test shows viewer window with two curves: one curve from the previous
        test must be cleared.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.set_scale(6.0, 6.0)

        x_1 = [-2.5, 0, 2.5]
        y_1 = [-0.005, 0, 0.005]
        curve_1 = window.plot.add_curve()
        curve_1.set_curve(Curve(x_1, y_1))
        curve_1.set_curve_param(QColor(255, 153, 102))

        x_2 = [-2.5, 0, 2.5]
        y_2 = [-0.003, 0, 0.003]
        curve_2 = window.plot.add_curve()
        curve_2.set_curve(Curve(x_2, y_2))
        curve_2.set_curve_param(QPen(QBrush(QColor(0, 153, 255)), 2))

        curve_1.clear_curve()
        self.assertTrue(curve_1.curve is None)

        window.setToolTip("Должна быть одна прямая")
        window.show()
        app.exec()
