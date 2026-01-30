import sys
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
try:
    import ivviewer
except ImportError:
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import ivviewer


app = QApplication(sys.argv)
window = ivviewer.Viewer(accuracy=2)
window.plot.set_x_axis_title("Название оси X")
window.plot.set_y_axis_title("Название оси Y")
window.plot.set_scale(6.0, 15.0)

x_test = [-2.5, 0, 2.5]
y_test = [-0.005, 0, 0.005]
test_curve = window.plot.add_curve("red")
test_curve.set_curve(ivviewer.Curve(x_test, y_test))
test_curve.set_curve_params(QColor("red"))

x_ref = [-2.5, 0, 2.5]
y_ref = [-0.003, 0, 0.0033]
reference_curve = window.plot.add_curve("green")
reference_curve.set_curve(ivviewer.Curve(x_ref, y_ref))
reference_curve.set_curve_params(QColor("green"))

window.resize(600, 600)
window.show()
app.exec()
