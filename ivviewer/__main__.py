from PyQt5.QtWidgets import QApplication
import sys
from .window import Viewer
from .ivcviewer import Curve


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Viewer()
    test_curve = window.plot.add_curve()
    reference_curve = window.plot.add_curve()

    x = [-2.5, 0, 2.5]
    y = [-0.005, 0, 0.005]

    x2 = [-2.5, 0, 2.5]
    y2 = [-0.003, 0, 0.0033]

    window.plot.set_scale(*(6.0, 15.0))
    test_curve.set_curve(Curve(x, y))
    reference_curve.set_curve(Curve(x2, y2))

    window.plot.set_center_text("DISCONNECTED")

    window.resize(600, 600)
    window.show()

    app.exec()
