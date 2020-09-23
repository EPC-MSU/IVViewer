import unittest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
import sys

from ivviewer import Viewer, Curve


class IVViewerTest(unittest.TestCase):
    def test_little_bit(self):
        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        test_curve = window.plot.add_curve()
        reference_curve = window.plot.add_curve()

        x = [-2.5, 0, 2.5]
        y = [-0.005, 0, 0.005]

        x2 = [-2.5, 0, 2.5]
        y2 = [-0.003, 0, 0.003]

        window.plot.set_scale(14.0, 28.0)
        test_curve.set_curve(Curve(x, y))
        reference_curve.set_curve(Curve(x2, y2))

        window.show()
        app.exec()

        self.assertTrue(True)

    def test_color_setup(self):
        app = QApplication(sys.argv)

        window = Viewer()
        window.setFixedSize(600, 600)
        test_curve = window.plot.add_curve()
        reference_curve = window.plot.add_curve()

        x = [-2.5, 0, 2.5]
        y = [0.005, 0, 0.005]

        x2 = [-2.5, 0, 2.5]
        y2 = [-0.003, 0, 0.003]

        test_curve.set_curve(Curve(x, y))
        reference_curve.set_curve(Curve(x2, y2))

        reference_curve.set_curve_params(color=QColor(0, 255, 255, 200))
        test_curve.set_curve_params(color=QColor(255, 0, 255, 400))

        window.show()
        app.exec()

        self.assertTrue(True)

    def test_three_curves(self):
        app = QApplication(sys.argv)

        window = Viewer()
        window.setFixedSize(600, 600)

        first_curve = window.plot.add_curve()
        second_curve = window.plot.add_curve()
        third_curve = window.plot.add_curve()
        x = [0, 1, 2]
        y = [-0.005, 0, 0.005]

        x2 = [3, 2, 5]
        y2 = [-0.003, 0, 0.003]

        x3 = [2, 3, 4]
        y3 = [-0.001, 0, 0.001]

        first_curve.set_curve(Curve(x, y))
        second_curve.set_curve(Curve(x2, y2))
        third_curve.set_curve(Curve(x3, y3))
        window.plot.set_scale(10.0, 20.0)
        first_curve.set_curve_params(color=QColor(255, 0, 255, 200))
        second_curve.set_curve_params(color=QColor(0, 255, 255, 200))
        third_curve.set_curve_params(color=QColor(255, 255, 0, 200))

        window.show()
        app.exec()

        self.assertTrue(True)
