import sys
import unittest
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication
from ivviewer import Curve, Viewer


class TestCurves(unittest.TestCase):

    def test_1_show_center_text(self) -> None:
        """
        Test checks that text is displayed in the center of plot.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        text = "В центре должен быть\nвыведен текст\nкрасного цвета"
        window.plot.set_center_text(text)
        window.setToolTip(text)
        self.assertTrue(window.plot._center_text_marker is not None)
        window.show()
        app.exec()

    def test_2_show_center_text_with_user_settings(self) -> None:
        """
        Test checks that text is displayed in the center of plot with user settings.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        font = QFont("Courier", 100)
        color = QColor(0, 153, 204)
        text = "В центре должен быть\nвыведен текст\nсинего цвета"
        window.plot.set_center_text(text, font, color)
        window.setToolTip(text)
        self.assertTrue(window.plot._center_text_marker is not None)
        window.show()
        app.exec()

    def test_3_remove_center_text(self) -> None:
        """
        Test checks that text in the center of plot is removed.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        text = "Не должно быть текста"
        window.plot.set_center_text(text)
        window.setToolTip(text)
        window.plot.clear_center_text()
        self.assertTrue(window.plot._center_text_marker is None)
        window.show()
        app.exec()

    def test_4_show_lower_text_with_user_settings(self) -> None:
        """
        Test checks that text is displayed in the lower part of plot with user settings.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        font = QFont("Courier", 100)
        color = QColor(0, 51, 0)
        text = "В нижней части графика должен быть\nзеленый текст"
        window.plot.set_lower_text(text, font, color)
        window.setToolTip(text)
        self.assertTrue(window.plot._lower_text_marker is not None)
        window.show()
        app.exec()

    def test_5_remove_lower_text(self) -> None:
        """
        Test checks that text in the lower part of plot is removed.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        text = "В нижней части графика не должно быть текста"
        window.plot.set_lower_text(text)
        window.setToolTip(text)
        window.plot.clear_lower_text()
        self.assertTrue(window.plot._lower_text_marker is None)
        window.show()
        app.exec()

    def test_6_disable_context_menu_for_cursors(self) -> None:
        """
        Test verifies that deactivation of cursors in the context menu works.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        window.plot.enable_context_menu_for_cursors(False)
        window.setToolTip("В контекстном меню не должно быть работы с метками")
        self.assertTrue(window.plot._context_menu_works_with_cursors is False)
        window.show()
        app.exec()

    def test_7_disable_context_menu(self) -> None:
        """
        Test checks that it is possible to deactivate the context menu.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        window.plot.enable_context_menu(False)
        window.setToolTip("Не должно отображаться контекстное меню")
        self.assertEqual(window.plot.contextMenuPolicy(), Qt.NoContextMenu)
        window.show()
        app.exec()

    def test_8_localize(self) -> None:
        """
        Test verifies that localization of context menu items works.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)
        window.plot.localize_widget(save_screenshot="Save image", add_cursor="Add cursor",
                                    remove_cursor="Remove cursor", remove_all_cursors="Remove all cursors")
        window.setToolTip("Контекстное меню должно отображаться на английском языке")
        self.assertEqual(window.plot._items_for_localization["save_screenshot"]["translation"], "Save image")
        window.show()
        app.exec()

    def test_9_set_axis_titles(self) -> None:
        """
        Test checks assignment of titles to axes.
        """

        app = QApplication(sys.argv)
        window = Viewer(x_title="Ось X", y_title="Ось Y", x_label="x", y_label="y", accuracy=3)
        window.setFixedSize(800, 600)
        window.plot.set_scale(6.0, 6.0)
        x_values = [-2.5, 0, 2.5]
        y_values = [-0.005, 0, 0.005]
        curve = window.plot.add_curve()
        curve.set_curve(Curve(x_values, y_values))
        curve.set_curve_params(QColor(255, 153, 102))
        window.plot.add_cursor(QPoint(222, 51))
        window.setToolTip("Оси должны иметь названия X и Y. Точность координаты метки - три знака")
        self.assertEqual(window.plot._x_title, "Ось X")
        self.assertEqual(window.plot._y_title, "Ось Y")
        window.show()
        app.exec()
