import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
try:
    import ivviewer
except ImportError:
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import ivviewer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._init_ui()

    @pyqtSlot()
    def _clear_curve(self) -> None:
        self.test_curve.clear_curve()

    def _create_buttons(self) -> None:
        self.button_clear_curve = QPushButton("Убрать кривую")
        self.button_clear_curve.clicked.connect(self._clear_curve)

        self.button_set_curve = QPushButton("Показать кривую")
        self.button_set_curve.clicked.connect(self._show_curve)

        self.button_hide_center_text = QPushButton("Скрыть текст в центре")
        self.button_hide_center_text.clicked.connect(self._hide_center_text)

        self.button_show_center_text = QPushButton("Показать текст в центре")
        self.button_show_center_text.clicked.connect(self._show_center_text)

        self.button_hide_low_text = QPushButton("Скрыть текст внизу")
        self.button_hide_low_text.clicked.connect(self._hide_lower_text)

        self.button_show_low_text = QPushButton("Показать текст внизу")
        self.button_show_low_text.clicked.connect(self._show_lower_text)

    def _create_viewer(self):
        self.viewer = ivviewer.Viewer(self)
        self.viewer.plot.set_x_axis_title("Название оси X")
        self.viewer.plot.set_y_axis_title("Название оси Y")
        self.viewer.plot.set_scale(6.0, 15.0)

        x_test = [-2.5, 0, 2.5]
        y_test = [-0.005, 0, 0.005]
        self.test_curve = self.viewer.plot.add_curve("red")
        self.test_curve.set_curve(ivviewer.Curve(x_test, y_test))
        self.test_curve.set_curve_params(QColor("red"))

        x_ref = [-2.5, 0, 2.5]
        y_ref = [-0.003, 0, 0.0033]
        self.reference_curve = self.viewer.plot.add_curve("green")
        self.reference_curve.set_curve(ivviewer.Curve(x_ref, y_ref))
        self.reference_curve.set_curve_params(QColor("green"))

        self.viewer.resize(600, 600)

    @pyqtSlot()
    def _hide_center_text(self) -> None:
        self.viewer.plot.clear_center_text()

    @pyqtSlot()
    def _hide_lower_text(self) -> None:
        self.viewer.plot.clear_lower_text()

    def _init_ui(self) -> None:
        self._create_viewer()
        self._create_buttons()

        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(self.button_clear_curve)
        layout.addWidget(self.button_set_curve)
        layout.addWidget(self.button_hide_center_text)
        layout.addWidget(self.button_show_center_text)
        layout.addWidget(self.button_hide_low_text)
        layout.addWidget(self.button_show_low_text)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @pyqtSlot()
    def _show_center_text(self) -> None:
        self.viewer.plot.set_center_text("Текст в центре")

    @pyqtSlot()
    def _show_curve(self) -> None:
        x_test = [-2.5, 0, 2.5]
        y_test = [-0.005, 0, 0.005]
        self.test_curve.set_curve(ivviewer.Curve(x_test, y_test))

    @pyqtSlot()
    def _show_lower_text(self) -> None:
        self.viewer.plot.set_lower_text("Текст внизу")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
