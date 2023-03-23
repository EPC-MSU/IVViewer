import os
import re
import sys
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication
from ivviewer import Curve, Viewer
from .utils import prepare_test


class TestViewer:

    @prepare_test
    def test_1_show_center_text(self, window: Viewer) -> None:
        """
        Test checks that text is displayed in the center of plot.
        :param window: viewer widget.
        """

        text = "В центре должен быть\nвыведен текст\nкрасного цвета"
        window.plot.set_center_text(text)
        window.setToolTip(text)
        assert window.plot._center_text_marker is not None
        label = window.plot._center_text_marker.label()
        assert label.text() == text
        assert label.color() == window.plot.DEFAULT_TEXT_COLOR

    @prepare_test
    def test_2_show_center_text_with_user_settings(self, window: Viewer) -> None:
        """
        Test checks that text is displayed in the center of plot with user settings.
        :param window: viewer widget.
        """

        font = QFont("", 30, -1, True)
        color = QColor(0, 153, 204)
        text = "В центре должен быть\nвыведен курсивом текст\nсинего цвета"
        window.plot.set_center_text(text, font, color)
        window.setToolTip(text)
        assert window.plot._center_text_marker is not None
        label = window.plot._center_text_marker.label()
        assert label.text() == text
        assert label.font() == font
        assert label.color() == color

    @prepare_test
    def test_3_remove_center_text(self, window: Viewer) -> None:
        """
        Test checks that text in the center of plot is removed.
        :param window: viewer widget.
        """

        text = "Не должно быть текста"
        window.plot.set_center_text(text)
        window.setToolTip(text)
        window.plot.clear_center_text()
        assert window.plot._center_text_marker is None

    @prepare_test
    def test_4_show_lower_text_with_user_settings(self, window: Viewer) -> None:
        """
        Test checks that text is displayed in the lower part of plot with user settings.
        :param window: viewer widget.
        """

        font = QFont("", 20, 3, True)
        color = QColor(0, 51, 0)
        text = "В нижней части графика должен быть\nкурсивный зеленый текст"
        window.plot.set_lower_text(text, font, color)
        window.setToolTip(text)
        assert window.plot._lower_text_marker is not None
        label = window.plot._lower_text_marker.label()
        assert label.text() == text
        assert label.font() == font
        assert label.color() == color

    @prepare_test
    def test_5_remove_lower_text(self, window: Viewer) -> None:
        """
        Test checks that text in the lower part of plot is removed.
        :param window: viewer widget.
        """

        text = "В нижней части графика не должно быть текста"
        window.plot.set_lower_text(text)
        window.setToolTip(text)
        window.plot.clear_lower_text()
        assert window.plot._lower_text_marker is None

    @prepare_test
    def test_6_disable_context_menu_for_cursors(self, window: Viewer) -> None:
        """
        Test verifies that deactivation of cursors in the context menu works.
        :param window: viewer widget.
        """

        window.plot.enable_context_menu_for_cursors(False)
        window.setToolTip("В контекстном меню не должно быть работы с метками")
        assert window.plot._context_menu_works_with_cursors is False

    @prepare_test
    def test_7_disable_context_menu(self, window: Viewer) -> None:
        """
        Test checks that it is possible to deactivate the context menu.
        :param window: viewer widget.
        """

        window.plot.enable_context_menu(False)
        window.setToolTip("Не должно отображаться контекстное меню")
        assert window.plot.contextMenuPolicy() == Qt.NoContextMenu

    @prepare_test
    def test_8_localize(self, window: Viewer) -> None:
        """
        Test verifies that localization of context menu items works.
        :param window: viewer widget.
        """

        window.plot.localize_widget(add_cursor="Add cursor", export_ivc="Export IVC to file",
                                    remove_all_cursors="Remove all cursors", remove_cursor="Remove cursor",
                                    save_screenshot="Save image")
        window.setToolTip("Контекстное меню должно отображаться на английском языке")
        assert window.plot._items_for_localization["add_cursor"]["translation"] == "Add cursor"
        assert window.plot._items_for_localization["export_ivc"]["translation"] == "Export IVC to file"
        assert window.plot._items_for_localization["remove_all_cursors"]["translation"] == "Remove all cursors"
        assert window.plot._items_for_localization["remove_cursor"]["translation"] == "Remove cursor"
        assert window.plot._items_for_localization["save_screenshot"]["translation"] == "Save image"

    def test_9_set_axis_titles_in_constructor(self, display_window: bool) -> None:
        """
        Test checks assignment of titles to axes.
        :param display_window: if True then widget will be displayed.
        """

        app = QApplication(sys.argv)
        window = Viewer(x_title="Ось X", y_title="Ось Y", x_label="x", y_label="y", accuracy=3)
        window.setFixedSize(800, 600)
        window.plot.add_cursor(QPoint(222, 51))
        window.setToolTip("Оси должны иметь названия X и Y. Точность координаты метки - три знака")
        assert window.plot._x_title == "Ось X"
        assert window.plot._y_title == "Ось Y"
        for cursor in window.plot.cursors.cursors:
            assert cursor._accuracy == 3
            assert cursor._x_label == "x"
            assert cursor._y_label == "y"

        if display_window:
            window.show()
            app.exec()

    @prepare_test
    def test_10_set_axis_titles_by_method(self, window: Viewer) -> None:
        """
        Test checks assignment of titles to axes.
        :param window: viewer widget.
        """

        window.plot.add_cursor(QPoint(222, 51))
        window.plot.set_x_axis_title("Ось X", "x")
        window.plot.set_y_axis_title("Ось Y", "y")
        window.setToolTip("Оси должны иметь названия X и Y")
        assert window.plot._x_title == "Ось X"
        assert window.plot._y_title == "Ось Y"
        for cursor in window.plot.get_list_of_all_cursors():
            assert cursor._x_label == "x"
            assert cursor._y_label == "y"

    @prepare_test
    def test_11_save_screenshot(self, window: Viewer) -> None:
        """
        Test checks if screenshot is saved.
        :param window: viewer widget.
        """

        dir_to_save = os.path.join(os.path.curdir, "test_results")
        window.plot.set_path_to_directory(dir_to_save)
        files_before = set(os.listdir(dir_to_save))
        window.plot.save_image(False)
        window.setToolTip("В папке test_results должно появиться png изображение")
        files_after = set(os.listdir(dir_to_save))
        new_files = files_after.difference(files_before)
        assert len(new_files) == 1
        assert re.match(r"^image_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$", new_files.pop())

    @prepare_test
    def test_12_export_ivc(self, window: Viewer) -> None:
        """
        Test
        :param window: viewer widget.
        """

        x_values = [-2.5, 2.5]
        y_values = [-0.005, 0.005]
        curve = window.plot.add_curve()
        curve.set_curve(Curve(x_values, y_values))

        dir_to_export = os.path.join(os.path.curdir, "test_results")
        window.plot.set_path_to_directory(dir_to_export)
        files_before = set(os.listdir(dir_to_export))
        window.plot.export_ivc(False)
        window.setToolTip("В папке test_results должен появиться csv файл")
        files_after = set(os.listdir(dir_to_export))
        new_files = files_after.difference(files_before)
        assert len(new_files) == 1
        file_name = new_files.pop()
        assert re.match(r"^ivc_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$", file_name)

        with open(os.path.join(dir_to_export, file_name), "r") as file:
            content = file.read()
        assert content == "\ncurve #1:\nВ, А\n-2.5, -0.005\n2.5, 0.005\n"
