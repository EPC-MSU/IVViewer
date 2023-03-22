"""
File with example how to use Viewer.
"""

import sys
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from ivviewer.curve import Curve
from ivviewer.window import Viewer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Viewer()
    window.plot.set_scale(6.0, 15.0)
    window.plot.set_x_axis_title("Ось X", "x")
    window.plot.set_y_axis_title("Ось Y", "y")

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

    window.resize(600, 600)
    window.show()
    app.exec()
