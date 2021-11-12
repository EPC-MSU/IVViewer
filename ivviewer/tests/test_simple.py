import sys
import unittest
import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from ivviewer import Curve, Viewer


class IVViewerTest(unittest.TestCase):

    def test_1_two_curves(self):
        """
        Test shows viewer window with two straight lines. Viewer is scaled
        to show both lines.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.set_scale(14.0, 28.0)

        x_test = [-2.5, 0, 2.5]
        y_test = [-0.005, 0, 0.005]
        test_curve = window.plot.add_curve()
        test_curve.set_curve(Curve(x_test, y_test))

        x_ref = [-2.5, 0, 2.5]
        y_ref = [-0.003, 0, 0.003]
        reference_curve = window.plot.add_curve()
        reference_curve.set_curve(Curve(x_ref, y_ref))

        window.show()
        app.exec()
        self.assertTrue(True)

    def test_2_two_curves_with_color_setup(self):
        """
        Test shows viewer window with two straight lines and sets colors for lines.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)

        x_test = [-2.5, 0, 2.5]
        y_test = [0.005, 0, 0.005]
        test_curve = window.plot.add_curve()
        test_curve.set_curve(Curve(x_test, y_test))
        test_curve.set_curve_params(color=QColor(255, 0, 255, 400))

        x_ref = [-2.5, 0, 2.5]
        y_ref = [-0.003, 0, 0.003]
        reference_curve = window.plot.add_curve()
        reference_curve.set_curve(Curve(x_ref, y_ref))
        reference_curve.set_curve_params(color=QColor(0, 255, 255, 200))

        window.show()
        app.exec()
        self.assertTrue(True)

    def test_3_three_curves_with_color_setup(self):
        """
        Test shows viewer window with three curves and sets colors for lines.
        Viewer is scaled to show all lines.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.set_scale(10.0, 20.0)

        x_first = [0, 1, 2]
        y_first = [-0.005, 0, 0.005]
        first_curve = window.plot.add_curve()
        first_curve.set_curve(Curve(x_first, y_first))
        first_curve.set_curve_params(color=QColor(255, 0, 255, 200))

        x_second = [3, 2, 5]
        y_second = [-0.003, 0, 0.003]
        second_curve = window.plot.add_curve()
        second_curve.set_curve(Curve(x_second, y_second))
        second_curve.set_curve_params(color=QColor(0, 255, 255, 200))

        x_third = [2, 3, 4]
        y_third = [-0.001, 0, 0.001]
        third_curve = window.plot.add_curve()
        third_curve.set_curve(Curve(x_third, y_third))
        third_curve.set_curve_params(color=QColor(255, 255, 0, 200))

        window.show()
        app.exec()
        self.assertTrue(True)

    def test_4_context_menu_with_center_text(self):
        """
        Test shows viewer window with text in center. And context menu is disabled
        (context menu will not appear on right-click).
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        window.plot.set_center_text("Context menu is disabled")
        window.show()
        app.exec()
        self.assertTrue(True)

    def test_5_markers(self):
        """
        Test shows viewer window with one curve and two markers.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.set_scale(14.0, 28.0)

        angle = np.linspace(0, 2 * np.pi, 100)
        radius = 5.0
        x = radius * np.cos(angle)
        y = 0.001 * radius * np.sin(angle)
        curve = window.plot.add_curve()
        curve.set_curve(Curve(x, y))

        window.plot.add_cursor(QPoint(22, 51))
        window.plot.add_cursor(QPoint(350, 203))

        window.show()
        app.exec()
        self.assertTrue(len(window.plot.get_list_of_all_cursors()) == 2)
