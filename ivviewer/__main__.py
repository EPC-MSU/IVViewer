from PyQt5.QtWidgets import QApplication
import sys
from .window import Viewer
from .ivcviewerconstants import adjust_scale, Voltage, Current
from .ivcviewer import Curve


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Viewer()

    x = [-2.5, 0, 2.5]
    y = [-5, 0, 5]

    x2 = [-2.5, 0, 2.5]
    y2 = [-3, 0, 3]

    window.plot.set_scale(*adjust_scale(Voltage.VOLTAGE_3_3V, Current.CURRENT_25MA))
    window.plot.set_test_curve(Curve(x, y))
    window.plot.set_reference_curve(Curve(x2, y2))

    window.resize(600, 600)
    window.show()

    app.exec()
