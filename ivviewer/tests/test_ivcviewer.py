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
        window.plot.set_center_text("Context menu is disabled")
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
        window.plot.set_center_text("Blue central text", font, color)
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
        window.plot.set_center_text("Context menu is disabled")
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
        window.plot.set_lower_text("Green lower text", font, color)
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
        window.plot.set_lower_text("Green lower text")
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
        self.assertEqual(window.plot._items_for_localization["save_screenshot"]["translation"], "Save image")
        window.show()
        app.exec()

    def test_9_set_axis_titles(self) -> None:
        """
        Test checks assignment of titles to axes.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(800, 600)

        x_values = [-2.5, 0, 2.5]
        y_values = [-0.005, 0, 0.005]
        curve = window.plot.add_curve()
        curve.set_curve(Curve(x_values, y_values))
        curve.set_curve_param(QColor(255, 153, 102))
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.set_axis_titles("Ось X", "Ось Y", "x", "y")
        self.assertEqual(window.plot._x_title, "Ось X")
        self.assertEqual(window.plot._y_title, "Ось Y")
        window.show()
        app.exec()
