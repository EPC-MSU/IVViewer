import sys
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from ivviewer import Viewer
from ivviewer.ivcviewer import Point
from .utils import MouseEvent, prepare_test


class TestCursor:

    @prepare_test
    def test_1_add_cursor(self, window: Viewer) -> None:
        """
        Test checks for adding a cursor.
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.setToolTip("Должно быть две метки. Активная метка (красная) - та, что правее и ниже")
        assert len(window.plot.get_list_of_all_cursors()) == 2
        assert window.plot.cursors._current_index == 1

    @prepare_test
    def test_2_remove_cursor(self, window: Viewer) -> None:
        """
        Test checks for removal of current cursor.
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.plot.remove_cursor()
        window.setToolTip("Должна быть одна неактивная метка (зеленая)")
        assert len(window.plot.get_list_of_all_cursors()) == 1
        assert window.plot.cursors._current_index is None

    @prepare_test
    def test_3_remove_all_cursors(self, window: Viewer) -> None:
        """
        Test checks for removal of all cursors.
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        window.plot.remove_all_cursors()
        window.setToolTip("Не должно быть ни одной метки")
        assert len(window.plot.get_list_of_all_cursors()) == 0
        assert window.plot.cursors._current_index is None

    @prepare_test
    def test_4_change_current_cursor(self, window: Viewer) -> None:
        """
        Test checks that the current cursor has changed.
        :param window: viewer widget.
        """

        pos = QPoint(222, 51)
        window.plot.add_cursor(pos)
        window.plot.add_cursor(QPoint(450, 303))
        event = MouseEvent(pos)
        window.plot.mousePressEvent(event)
        window.setToolTip("Должно быть две метки. Активная метка (красная) - та, что левее и выше")
        assert window.plot.cursors._current_index == 0

    @prepare_test
    def test_5_no_current_cursor(self, window: Viewer) -> None:
        """
        Test checks that if you click in the plot and do not hit any cursor, then none of the cursor will be current
        cursor.
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        event = MouseEvent(QPoint(300, 400))
        window.plot.mousePressEvent(event)
        window.setToolTip("Должно быть две неактивные метки (зеленые)")
        assert window.plot.cursors._current_index is None

    @prepare_test
    def test_6_move_cursor(self, window: Viewer) -> None:
        """
        Test checks the movement of the current cursor. Current cursor is second cursor (with index 1).
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(450, 303))
        x_to_move = 0.5
        y_to_move = -0.2
        window.plot.cursors.move_cursor(Point(x_to_move, y_to_move))
        current_index = window.plot.cursors._current_index
        current_cursor = window.plot.get_list_of_all_cursors()[current_index]
        window.setToolTip(f"Должно быть две метки. Активная метка (красная) должна находиться в точке ({x_to_move}, "
                          f"{y_to_move})")
        assert current_cursor.x == x_to_move
        assert current_cursor.y == y_to_move

    def test_7_set_colors_for_cursors(self, display_window: bool) -> None:
        """
        Test checks for setting colors for cursors.
        :param display_window: if True then widget will be displayed.
        """

        app = QApplication(sys.argv)
        window = Viewer(color_for_rest_cursors=QColor(153, 0, 51), color_for_selected_cursor=QColor(102, 0, 204))
        window.setFixedSize(600, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.plot.add_cursor(QPoint(350, 103))
        window.setToolTip("Должно быть две метки: темно-красная и темно-синяя")
        cursors = window.plot.get_list_of_all_cursors()
        assert len(cursors) == 2
        assert window.plot.cursors._current_index == 1
        assert cursors[0]._x_axis.pen().color() == window.plot.cursors._color_for_rest
        assert cursors[1]._x_axis.pen().color() == window.plot.cursors._color_for_selected
        if display_window:
            window.show()
            app.exec()
