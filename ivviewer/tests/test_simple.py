import unittest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
import sys

from ivviewer import Viewer, Curve


class IVViewerTest(unittest.TestCase):
    def test_little_bit(self):
        app = QApplication(sys.argv)
        window = Viewer()
        test_curve = window.plot.add_curve()
        reference_curve = window.plot.add_curve()

        x = [-2.5, 0, 2.5]
        y = [-5, 0, 5]

        x2 = [-2.5, 0, 2.5]
        y2 = [-3, 0, 3]

        window.plot.set_scale(14.0, 28.0)
        test_curve.set_curve(Curve(x, y))
        reference_curve.set_curve(Curve(x2, y2))

        app.exit(0)
        self.assertTrue(True)

    def test_color_setup(self):
        app = QApplication(sys.argv)

        window = Viewer()
        test_curve = window.plot.add_curve()
        reference_curve = window.plot.add_curve()

        x = [-2.5, 0, 2.5]
        y = [-5, 0, 5]

        x2 = [-2.5, 0, 2.5]
        y2 = [-3, 0, 3]

        test_curve.set_curve(Curve(x, y))
        reference_curve.set_curve(Curve(x2, y2))

        reference_curve.set_curve_params(color=QColor(0, 255, 255, 200))
        test_curve.set_curve_params(color=QColor(255, 0, 255, 400))

        app.exit(0)
        self.assertTrue(True)

    def test_three_curves(self):
        app = QApplication(sys.argv)

        window = Viewer()
        first_curve = window.plot.add_curve()
        second_curve = window.plot.add_curve()
        third_curve = window.plot.add_curve()

        x = [-2.5, 0, 2.5]
        y = [-5, 0, 5]

        x2 = [-2.5, 0, 2.5]
        y2 = [-3, 0, 3]

        x3 = [-2.5, 0, 2.5]
        y3 = [-1, 0, 1]

        first_curve.set_curve(Curve(x, y))
        second_curve.set_curve(Curve(x2, y2))
        third_curve.set_curve(Curve(x3, y3))

        third_curve.set_curve_params(color=QColor(255, 0, 255, 400))

        app.exit(0)
        self.assertTrue(True)
