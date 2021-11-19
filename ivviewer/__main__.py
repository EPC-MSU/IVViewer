"""
File with example how to use Viewer.
"""

import sys
import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication
from .ivcviewer import Curve
from .window import Viewer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Viewer(axis_font=QFont("Lucida Console", 10), marker_font=QFont("Times", 15),
                    title_font=QFont("Monaco", 30))
    window.plot.set_x_axis_title("Напряжение, В")
    window.plot.set_y_axis_title("Ток, мА")
    window.plot.set_scale(6.0, 15.0)

    # Add three curves
    x_test = [-2.5, 0, 2.5]
    y_test = [-0.005, 0, 0.005]
    test_curve = window.plot.add_curve()
    test_curve.set_curve(Curve(x_test, y_test))
    test_curve.set_curve_params(QColor("red"))

    x_ref = [-2.5, 0, 2.5]
    y_ref = [-0.003, 0, 0.0033]
    reference_curve = window.plot.add_curve()
    reference_curve.set_curve(Curve(x_ref, y_ref))
    reference_curve.set_curve_params(QColor("green"))

    angle = np.linspace(0, 2 * np.pi, 100)
    radius = 1.0
    x_third = radius * np.cos(angle)
    y_third = 0.001 * radius * np.sin(angle)
    third_curve = window.plot.add_curve()
    third_curve.set_curve(Curve(x_third, y_third))
    third_curve.set_curve_params(QColor("blue"))

    # Add cursors
    window.plot.add_cursor(QPoint(22, 51))
    window.plot.add_cursor(QPoint(350, 203))

    # Set text in center of viewer
    # window.plot.set_center_text("DISCONNECTED")

    window.resize(600, 600)
    window.show()

    app.exec()
