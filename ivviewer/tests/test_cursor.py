import sys
import unittest
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from ivviewer import Viewer
from ivviewer.ivcviewer import Point


class MouseEvent:

    def __init__(self, pos: QPoint) -> None:
        self._pos = pos

    def accept(self) -> None:
        pass

    def button(self) -> int:
        return Qt.LeftButton

    def pos(self) -> QPoint:
        return self._pos


class TestCurves(unittest.TestCase):

    def test_1_add_cursor(self) -> None:
        """
        Test checks for adding a cursor. Test shows viewer window with one curve and two cursors.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.setToolTip("Должно быть две метки. Активная метка (красная) - та, что правее и ниже")
        self.assertEqual(len(window.plot.get_list_of_all_cursors()), 2)
        self.assertEqual(window.plot.cursors._current_index, 1)
        window.show()
        app.exec()

    def test_2_remove_cursor(self) -> None:
        """
        Test checks for removal of current cursor. Test shows viewer window with one curve and one cursor.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.plot.remove_cursor()
        window.setToolTip("Должна быть одна неактивная метка (зеленая)")
        self.assertEqual(len(window.plot.get_list_of_all_cursors()), 1)
        self.assertTrue(window.plot.cursors._current_index is None)
        window.show()
        app.exec()

    def test_3_remove_all_cursors(self) -> None:
        """
        Test checks for removal of all cursors. Test shows viewer window with one curve and without cursors.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.plot.remove_all_cursors()
        window.setToolTip("Не должно быть ни одной метки")
        self.assertEqual(len(window.plot.get_list_of_all_cursors()), 0)
        self.assertTrue(window.plot.cursors._current_index is None)
        window.show()
        app.exec()

    def test_4_change_current_cursor(self) -> None:
        """
        Test checks that the current cursor has changed. Test shows viewer window with one curve and two cursors.
        After a virtual mouse click, first cursor (with index 0) becomes current cursor.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        pos = QPoint(222, 51)
        window.plot.add_cursor(pos)
        window.plot.add_cursor(QPoint(450, 303))
        event = MouseEvent(pos)
        window.plot.mousePressEvent(event)
        window.setToolTip("Должно быть две метки. Активная метка (красная) - та, что левее и выше")
        self.assertEqual(window.plot.cursors._current_index, 0)
        window.show()
        app.exec()

    def test_5_no_current_cursor(self) -> None:
        """
        Test checks that if you click in the plot and do not hit any cursor, then none of the cursor will be current
        cursor. Test shows viewer window with one curve and two cursors.
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        event = MouseEvent(QPoint(300, 400))
        window.plot.mousePressEvent(event)
        window.setToolTip("Должно быть две неактивные метки (зеленые)")
        self.assertTrue(window.plot.cursors._current_index is None)
        window.show()
        app.exec()

    def test_6_move_cursor(self) -> None:
        """
        Test checks the movement of the current cursor. Current cursor is second cursor (with index 1).
        """

        app = QApplication(sys.argv)
        window = Viewer()
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        x_to_move = 0.5
        y_to_move = -0.2
        window.plot.cursors.move_cursor(Point(x_to_move, y_to_move))
        current_index = window.plot.cursors._current_index
        current_cursor = window.plot.get_list_of_all_cursors()[current_index]
        window.setToolTip(f"Должно быть две метки. Активная метка (красная) должна находиться в точке ({x_to_move}, "
                          f"{y_to_move})")
        self.assertEqual(current_cursor.x, x_to_move)
        self.assertEqual(current_cursor.y, y_to_move)
        window.show()
        app.exec()

    def test_7_set_colors_for_cursors(self) -> None:
        """
        Test checks for setting colors for cursors. Test shows viewer window with one curve and three cursors.
        """

        app = QApplication(sys.argv)
        window = Viewer(color_for_rest_cursors=QColor(153, 0, 51), color_for_selected_cursor=QColor(102, 0, 204))
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.plot.add_cursor(QPoint(350, 103))
        window.setToolTip("Должно быть две метки темно-красные и одна метка темно-синяя")
        self.assertEqual(len(window.plot.get_list_of_all_cursors()), 3)
        self.assertEqual(window.plot.cursors._current_index, 2)
        window.show()
        app.exec()
