import unittest

from PyQt5.QtWidgets import QApplication
import sys

from ivviewer import Viewer, Curve


class IVViewerTest(unittest.TestCase):
    def test_little_bit(self):
        app = QApplication(sys.argv)

        window = Viewer()

        x = [-2.5, 0, 2.5]
        y = [-5, 0, 5]

        x2 = [-2.5, 0, 2.5]
        y2 = [-3, 0, 3]

        window.plot.set_scale(14.0, 28.0)
        window.plot.set_test_curve(Curve(x, y))
        window.plot.set_reference_curve(Curve(x2, y2))
        app.exit(0)
        self.assertTrue(True)
