import os
import platform
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Tuple
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication as qApp, QEvent, QObject, QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QMouseEvent, QPen
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from qwt import QwtLegend, QwtPlot, QwtPlotGrid, QwtPlotMarker, QwtText
from ivviewer.cursor import IvcCursor, IvcCursors
from ivviewer.curve import Curve, PlotCurve, Point


class IvcViewer(QwtPlot):

    DEFAULT_AXIS_FONT_SIZE: int = 20
    DEFAULT_BACK_COLOR: QColor = QColor(0xe1, 0xed, 0xeb)
    DEFAULT_CENTER_TEXT_FONT_SIZE: int = 40
    DEFAULT_GRID_COLOR: QColor = QColor(0, 0, 0)
    DEFAULT_LOWER_TEXT_FONT_SIZE: int = 10
    DEFAULT_TEXT_COLOR: QColor = QColor(255, 0, 0)
    DEFAULT_TITLE_FONT_SIZE: int = 20
    DEFAULT_X_TITLE: str = "Напряжение, В"
    DEFAULT_X_UNIT: str = "В"
    DEFAULT_Y_TITLE: str = "Ток, мА"
    DEFAULT_Y_UNIT: str = "А"
    MIN_BORDER_Y: float = 0.5
    MIN_BORDER_X: float = 1.0
    curve_changed: pyqtSignal = pyqtSignal()
    min_borders_changed: pyqtSignal = pyqtSignal()

    def __init__(self, owner, parent=None, solid_axis_enabled: bool = True, grid_color: QColor = None,
                 back_color: QColor = None, text_color: QColor = None, color_for_rest_cursors: QColor = None,
                 color_for_selected_cursor: QColor = None, axis_label_enabled: bool = True,
                 axis_font: QFont = None, cursor_font: QFont = None, title_font: QFont = None, x_title: str = None,
                 y_title: str = None, x_label: str = None, y_label: str = None, x_unit: str = None, y_unit: str = None,
                 accuracy: int = None) -> None:
        """
        :param owner: owner widget;
        :param parent: parent widget;
        :param solid_axis_enabled: if True then axes will be shown with solid lines;
        :param grid_color: grid color;
        :param back_color: canvas background color;
        :param text_color: color of text at the center of plot;
        :param color_for_rest_cursors: color for unselected cursors;
        :param color_for_selected_cursor: color for selected cursor;
        :param axis_label_enabled: if True then labels of axes will be displayed;
        :param axis_font: font for values on axes;
        :param cursor_font: font of text at cursors;
        :param title_font: axis titles font;
        :param x_title: title for horizontal axis;
        :param y_title: title for vertical axis;
        :param x_label: short name for horizontal axis;
        :param y_label: short name for vertical axis;
        :param x_unit: unit of measure for the value along horizontal axis;
        :param y_unit: unit of measure for the value along vertical axis;
        :param accuracy: the accuracy with which you want to display coordinate values on cursors.
        """

        super().__init__(parent)
        self._owner = owner
        self._axis_font: QFont = axis_font if isinstance(axis_font, QFont) else QFont("", self.DEFAULT_AXIS_FONT_SIZE)
        self._grid_color: QColor = grid_color if isinstance(grid_color, QColor) else self.DEFAULT_GRID_COLOR
        self._text_color: QColor = text_color if isinstance(text_color, QColor) else self.DEFAULT_TEXT_COLOR
        self._title_font: QFont = title_font if isinstance(title_font, QFont) else \
            QFont("", self.DEFAULT_TITLE_FONT_SIZE)

        self.__grid: QwtPlotGrid = QwtPlotGrid()
        self.__grid.enableXMin(True)
        self.__grid.enableYMin(True)
        if solid_axis_enabled:
            self.__grid.setMajorPen(QPen(self._grid_color, 0, Qt.SolidLine))
        else:
            self.__grid.setMajorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        self.__grid.setMinorPen(QPen(QColor(128, 128, 128), 0, Qt.DotLine))
        # self.__grid.updateScaleDiv(20, 30)
        self.__grid.attach(self)

        back_color = back_color if isinstance(back_color, QColor) else self.DEFAULT_BACK_COLOR
        self.setCanvasBackground(QBrush(back_color, Qt.SolidPattern))
        self.canvas().setCursor(QCursor(Qt.ArrowCursor))
        # Initial setup for axis scales
        self._min_border_x: float = abs(float(IvcViewer.MIN_BORDER_X))
        self._min_border_y: float = abs(float(IvcViewer.MIN_BORDER_Y))
        self._x_scale: float = None
        self._y_scale: float = None
        # X Axis
        axis_pen = QPen(QBrush(self._grid_color), 2)
        self._xy_axis: QwtPlotMarker = QwtPlotMarker()
        self._xy_axis.setLinePen(axis_pen)
        self._xy_axis.setLineStyle(QwtPlotMarker.Cross)
        self._xy_axis.setValue(0, 0)
        self._xy_axis.setZ(0)
        self._xy_axis.attach(self)

        self._x_label: str = x_label
        self._x_title: str = x_title if x_title is not None else self.DEFAULT_X_TITLE
        self._x_unit: str = x_unit if x_unit is not None else self.DEFAULT_X_UNIT
        self.setAxisFont(QwtPlot.xBottom, self._axis_font)
        self.setAxisMaxMajor(QwtPlot.xBottom, 5)
        self.setAxisMaxMinor(QwtPlot.xBottom, 5)
        # Y Axis
        self._y_label: str = y_label
        self._y_title: str = y_title if y_title is not None else self.DEFAULT_Y_TITLE
        self._y_unit: str = y_unit if y_unit is not None else self.DEFAULT_Y_UNIT
        self.setAxisFont(QwtPlot.yLeft, self._axis_font)
        self.setAxisMaxMajor(QwtPlot.yLeft, 5)
        self.setAxisMaxMinor(QwtPlot.yLeft, 5)

        self.enableAxis(QwtPlot.xBottom, axis_label_enabled)
        self.enableAxis(QwtPlot.yLeft, axis_label_enabled)

        self.cursors: IvcCursors = IvcCursors(self, cursor_font, color_for_rest=color_for_rest_cursors,
                                              color_for_selected=color_for_selected_cursor, x_label=x_label,
                                              y_label=y_label, accuracy=accuracy)
        self.curves: List[PlotCurve] = []
        self._center_text: QwtText = None
        self._center_text_marker: QwtPlotMarker = None
        self._lower_text: QwtText = None
        self._lower_text_marker: QwtPlotMarker = None

        self._add_cursor_mode: bool = False
        self._remove_cursor_mode: bool = False

        self._context_menu_works_with_cursors: bool = True
        self._dir_path: str = "."
        self.enable_context_menu(True)

        self._items_for_localization: Dict[str, Dict[str, str]] = {
            "add_cursor": {"default": "Добавить метку"},
            "export_ivc": {"default": "Экспортировать кривые в файл"},
            "remove_all_cursors": {"default": "Удалить все метки"},
            "remove_cursor": {"default": "Удалить метку"},
            "save_screenshot": {"default": "Сохранить изображение"},
        }
        self._left_button_pressed: bool = False
        self._set_axis_titles()
        self._adjust_scale()

        self.setMouseTracking(True)
        canvas = self.canvas()
        canvas.setMouseTracking(True)
        canvas.installEventFilter(self)

    @property
    def x_scale(self) -> float:
        """
        :return: maximum value (scale) along horizontal X axis.
        """

        return self._get_scale(self._x_scale, self._min_border_x)

    @property
    def y_scale(self) -> float:
        """
        :return: maximum value (scale) along horizontal Y axis.
        """

        return self._get_scale(self._y_scale, self._min_border_y)

    def _adjust_scale(self) -> None:
        """
        Method disables autoscaling and specifies a fixed scales for axes.
        """

        x_scale = self.x_scale
        y_scale = self.y_scale
        self.setAxisScale(QwtPlot.xBottom, -x_scale, x_scale)
        self.setAxisScale(QwtPlot.yLeft, -y_scale, y_scale)
        self._update_align_lower_text(x_scale, y_scale)

    def _change_mouse_cursor(self, cursor_under_mouse: Optional[bool] = None) -> None:
        """
        :param cursor_under_mouse: True if the mouse is pointing at the cursor.
        """

        if self._left_button_pressed:
            mouse_cursor = QCursor(Qt.ClosedHandCursor)
        elif cursor_under_mouse:
            mouse_cursor = QCursor(Qt.PointingHandCursor)
        else:
            mouse_cursor = None
        self._set_mouse_cursor(mouse_cursor)

    def _check_cursor_under_mouse(self, pos) -> bool:
        """
        :param pos: mouse position.
        :return: True if the mouse is hovering over a cursor.
        """

        cursor_index = self.cursors.find_cursor_at_point(pos)
        return self.cursors[cursor_index] is not None

    def _get_default_path(self, file_base_name: str, extension: str) -> str:
        """
        :param file_base_name: main file name;
        :param extension: file extension.
        :return: default file path.
        """

        file_name = file_base_name + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + extension
        if not os.path.isdir(self._dir_path):
            os.makedirs(self._dir_path)
        return os.path.join(self._dir_path, file_name)

    def _get_item_label(self, item_name: str) -> str:
        """
        :param item_name: context menu item.
        :return: text for the context menu item.
        """

        item = self._items_for_localization.get(item_name, {})
        translation = item.get("translation", None)
        if translation is not None:
            return translation

        return item.get("default", "")

    @staticmethod
    def _get_scale(scale: float, min_border: float) -> float:
        """
        :param scale: scale;
        :param min_border: minimum acceptable axis scale.
        :return: permissible axis scale.
        """

        if isinstance(scale, (float, int)) and abs(scale) > abs(min_border):
            return abs(scale)

        return abs(min_border)

    def _handle_mouse_move_event(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        pos = self.canvas().mapToParent(event.pos())
        self._change_mouse_cursor(self._check_cursor_under_mouse(pos))
        if self._left_button_pressed:
            pos_to_move = self._transform_point_coordinates(pos)
            self.cursors.move_cursor(pos_to_move)

    def _set_axis_titles(self) -> None:
        x_axis_title = QwtText(self._x_title)
        x_axis_title.setFont(self._title_font)
        self.setAxisTitle(QwtPlot.xBottom, x_axis_title)

        y_axis_title = QwtText(self._y_title)
        y_axis_title.setFont(self._title_font)
        self.setAxisTitle(QwtPlot.yLeft, y_axis_title)

        self.cursors.set_axis_labels(self._x_label, self._y_label)

    @staticmethod
    def _set_mouse_cursor(mouse_cursor: Optional[QCursor] = None) -> None:
        """
        :param mouse_cursor: application overrider cursor.
        """

        app = qApp.instance()
        while app.overrideCursor():
            try:
                app.restoreOverrideCursor()
            except Exception:
                pass

        if mouse_cursor:
            app.setOverrideCursor(mouse_cursor)

    def _transform_point_coordinates(self, pos: QPoint) -> Point:
        """
        Method transforms the coordinates of a position in the drawing region into a
        :param pos: coordinates of a position in the drawing region.
        :return: transformed position at axes coordinates.
        """

        pos_x = pos.x() - self.canvas().x()
        pos_y = pos.y() - self.canvas().y()
        x = np.round(self.invTransform(QwtPlot.xBottom, pos_x), 2)
        y = np.round(self.invTransform(QwtPlot.yLeft, pos_y), 2)
        return Point(x, y)

    def _update_align_lower_text(self, x_scale: float, y_scale: float) -> None:
        """
        Method updates the position of the text at the bottom of the widget.
        :param x_scale: new X scale value;
        :param y_scale: new Y scale value.
        """

        if not self._lower_text:
            return

        self._lower_text_marker.setValue(-x_scale, -y_scale)

    @pyqtSlot(QPoint)
    def add_cursor(self, position: QPoint) -> None:
        """
        Slot adds cursor and positions it at a given point.
        :param position: point where cursor should be placed.
        """

        pos = self._transform_point_coordinates(position)
        self.cursors.add_cursor(pos)

    def add_curve(self, title: str = None) -> PlotCurve:
        """
        :param title: curve title.
        :return: added curve.
        """

        if title is None:
            title = f"curve #{len(self.curves) + 1}"
        curve = PlotCurve(self, title=title)
        curve.set_curve_params(QColor(255, 0, 0, 200))
        curve.attach(self)
        curve.curve_changed.connect(self.curve_changed.emit)
        self.curves.append(curve)
        return curve

    def check_non_empty_curves(self) -> bool:
        """
        Method checks if there are non-empty curves.
        :return: True if there are non-empty curves.
        """

        return any(not curve.is_empty() for curve in self.curves)

    def clear_center_text(self) -> None:
        """
        Method removes text from the center of the widget and returns the display of curves and axes.
        """

        if self._center_text_marker:
            self._center_text_marker.detach()
            self._center_text_marker = None
            self._center_text = None
            self.__grid.attach(self)
            self._xy_axis.attach(self)
            _ = [curve.attach(self) for curve in self.curves]
            self.cursors.attach(self)

    def clear_lower_text(self) -> None:
        """
        Method removes text from the bottom of the widget.
        """

        if self._lower_text_marker:
            self._lower_text_marker.detach()
            self._lower_text_marker = None
            self._lower_text = None

    def clear_min_borders(self) -> None:
        """
        Method removes user-specified minimum acceptable axis scales ​​and restores default values.
        """

        self._min_border_x = abs(float(IvcViewer.MIN_BORDER_X))
        self._min_border_y = abs(float(IvcViewer.MIN_BORDER_Y))
        self._adjust_scale()
        self.min_borders_changed.emit()

    def enable_context_menu(self, enable: bool) -> None:
        """
        :param enable: if True then context menu will be enabled.
        """

        if enable:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.show_context_menu)
        else:
            self.setContextMenuPolicy(Qt.NoContextMenu)
            try:
                self.customContextMenuRequested.disconnect()
            except Exception:
                pass

    def enable_context_menu_for_cursors(self, enable: bool) -> None:
        """
        :param enable: if True then context menu can work with cursors.
        """

        self._context_menu_works_with_cursors = enable

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        :param obj: the object for which the event occurred;
        :param event: event.
        :return:
        """

        if obj == self.canvas() and isinstance(event, QMouseEvent) and event.type() == QEvent.MouseMove:
            self._handle_mouse_move_event(QMouseEvent(event))
            return True

        return super().eventFilter(obj, event)

    @pyqtSlot()
    def export_ivc(self, ask_where_to_export: bool = True) -> None:
        """
        Slot exports IV curves to file.
        :param ask_where_to_export: if True, then you need to ask the user where exactly to export curves.
        """

        def print_to_file(file_, curve_label: str, curve_: Curve) -> None:
            print(f"\n{curve_label}:", file=file_)
            print(f"{self._x_unit}, {self._y_unit}", file=file_)
            for voltage, current in zip(curve_.voltages, curve_.currents):
                print(f"{voltage}, {current}", file=file_)

        default_file_name = self._get_default_path("ivc", ".csv")
        options = {}
        if platform.system().lower() != "windows":
            options["options"] = QFileDialog.DontUseNativeDialog
        if ask_where_to_export:
            file_name = QFileDialog.getSaveFileName(self, self._get_item_label("export_ivc"), default_file_name,
                                                    "CSV files (*.csv)", **options)[0]
        else:
            file_name = default_file_name

        if not file_name:
            return

        if not file_name.endswith(".csv"):
            file_name += ".csv"
        with open(file_name, "w") as file:
            for curve in self.curves:
                if curve is not None and not curve.is_empty():
                    print_to_file(file, curve.curve_title, curve.curve)

    def get_list_of_all_cursors(self) -> List[IvcCursor]:
        """
        Method returns list of all cursors.
        :return: list of all cursors.
        """

        return self.cursors.cursors

    def get_min_borders(self) -> Tuple[float, float]:
        """
        :return: minimum acceptable axes scales.
        """

        return self._min_border_x, self._min_border_y

    def get_minor_axis_step(self) -> Tuple[float, float]:
        """
        :return: width and height of rectangle of minor axes.
        """

        x_map = self.__grid.xScaleDiv().ticks(self.__grid.xScaleDiv().MinorTick)
        y_map = self.__grid.yScaleDiv().ticks(self.__grid.yScaleDiv().MinorTick)
        x_step = min([round(x_map[i + 1] - x_map[i], 2) for i in range(len(x_map) - 1)])
        y_step = min([round(y_map[i + 1] - y_map[i], 2) for i in range(len(y_map) - 1)])
        return x_step, y_step

    def get_state_adding_cursor(self) -> bool:
        """
        :return: True if the widget is in the state of adding cursors when the left mouse button is pressed.
        """

        return self._add_cursor_mode

    def get_state_removing_cursor(self) -> bool:
        """
        :return: True if the widget is in the state of removing cursors when the left mouse button is pressed.
        """

        return self._remove_cursor_mode

    def localize_widget(self, **kwargs) -> None:
        """
        :param kwargs: dictionary with translation for context menu items.
        """

        for item_name, item in self._items_for_localization.items():
            item["translation"] = kwargs.get(item_name, None)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        This event handler receives mouse press events for the widget.
        :param event: mouse press event.
        """

        event_pos = event.pos()
        if event.button() == Qt.LeftButton and not self._center_text_marker:
            self.cursors.set_current_cursor(event_pos)
            cursor_under_mouse = self._check_cursor_under_mouse(event_pos)
            if self._add_cursor_mode and not cursor_under_mouse:
                pos = self._transform_point_coordinates(event_pos)
                self.cursors.add_cursor(pos)
            elif self._add_cursor_mode and cursor_under_mouse:
                self._left_button_pressed = True
            elif self._remove_cursor_mode and cursor_under_mouse:
                self.cursors.remove_current_cursor()
                self._left_button_pressed = False
            elif not self._add_cursor_mode and not self._remove_cursor_mode and cursor_under_mouse:
                self._left_button_pressed = True
            self._change_mouse_cursor()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        This event handler receives mouse release events for the widget.
        :param event: mouse release event.
        """

        if event.button() == Qt.LeftButton and self._check_cursor_under_mouse(event.pos()):
            self._left_button_pressed = False
            self._change_mouse_cursor(True)
        event.accept()

    def redraw_cursors(self) -> None:
        """
        Method redraws cursors.
        """

        self.cursors.paint_current_cursor()

    @pyqtSlot()
    def remove_all_cursors(self) -> None:
        """
        Slot deletes all cursors.
        """

        self.cursors.remove_all_cursors()

    @pyqtSlot()
    def remove_cursor(self) -> None:
        """
        Slot deletes current cursor.
        """

        self.cursors.remove_current_cursor()

    @pyqtSlot()
    def save_image(self, ask_where_to_save: bool = True) -> None:
        """
        Slot saves graph as image.
        :param ask_where_to_save: if True, then you need to ask the user where exactly to save the image.
        """

        default_file_name = self._get_default_path("image", ".png")
        options = {}
        if platform.system().lower() != "windows":
            options["options"] = QFileDialog.DontUseNativeDialog
        if ask_where_to_save:
            file_name = QFileDialog.getSaveFileName(self, self._get_item_label("save_screenshot"), default_file_name,
                                                    "Images (*.png *.jpg *.bmp *.pdf *.svg)", **options)[0]
        else:
            file_name = default_file_name

        if not file_name:
            return

        extensions = ".png", ".jpg", ".bmp", ".pdf", ".svg"
        extension = os.path.splitext(file_name)[1]
        if extension not in extensions:
            file_name += ".png"
        self.exportTo(file_name)

    def set_center_text(self, text: str, font: QFont = None, color: QColor = None) -> None:
        """
        :param text: text to be shown in the center of the widget;
        :param font: font fot text;
        :param color: color for text.
        """

        if isinstance(self._center_text, QwtText) and self._center_text == QwtText(text):
            # Same text already here
            return

        self.clear_center_text()  # clear current text
        self.__grid.detach()
        self._xy_axis.detach()
        self.cursors.detach()
        _ = [curve.detach() for curve in self.curves]

        self._center_text = QwtText(text)
        self._center_text.setFont(font if isinstance(font, QFont) else QFont("", self.DEFAULT_CENTER_TEXT_FONT_SIZE))
        self._center_text.setColor(color if isinstance(color, QColor) else self._text_color)
        self._center_text_marker = QwtPlotMarker()
        self._center_text_marker.setValue(0, 0)
        self._center_text_marker.setLabel(self._center_text)
        self._center_text_marker.attach(self)

    def set_lower_text(self, text: str, font: QFont = None, color: QColor = None) -> None:
        """
        :param text: text to be shown at the bottom of the widget;
        :param font: font for text;
        :param color: color for text.
        """

        if isinstance(self._lower_text, QwtText) and self._lower_text == text:
            # Same text already here
            return

        self.clear_lower_text()  # Clear current text
        self._lower_text = QwtText(text)
        self._lower_text.setFont(font if isinstance(font, QFont) else QFont("", self.DEFAULT_LOWER_TEXT_FONT_SIZE))
        self._lower_text.setColor(color if isinstance(color, QColor) else self._grid_color)
        self._lower_text.setRenderFlags(Qt.AlignLeft)
        self._lower_text_marker = QwtPlotMarker()
        self._lower_text_marker.setSpacing(10)
        self._lower_text_marker.setLabelAlignment(Qt.AlignTop | Qt.AlignRight)
        self._lower_text_marker.setLabel(self._lower_text)
        self._lower_text_marker.attach(self)
        self._adjust_scale()

    def set_min_borders(self, min_x: float, min_y: float) -> None:
        """
        :param min_x: minimum acceptable X axis scale;
        :param min_y: minimum acceptable Y axis scale.
        """

        self._min_border_x = abs(float(min_x))
        self._min_border_y = abs(float(min_y))
        self._adjust_scale()
        self.min_borders_changed.emit()

    def set_path_to_directory(self, dir_path: str) -> None:
        """
        Method sets path to directory where screenshots and IV curves are saved by default.
        :param dir_path: default directory path.
        """

        if os.path.isdir(dir_path):
            self._dir_path = dir_path

    def set_scale(self, x_scale: float, y_scale: float) -> None:
        """
        :param x_scale: X axis scale;
        :param y_scale: Y axis scale.
        """

        self._x_scale = x_scale
        self._y_scale = y_scale
        self._adjust_scale()

    def set_state_adding_cursor(self, state: bool) -> None:
        """
        :param state: if True, then a state will be set in which a marker will be added when the left mouse button is
        pressed.
        """

        self._add_cursor_mode = state
        if state:
            self.set_state_removing_cursor(False)

    def set_state_removing_cursor(self, state: bool) -> None:
        """
        :param state: if True, then a state will be set in which a marker will be removed when the left mouse button is
        pressed.
        """

        self._remove_cursor_mode = state
        if state:
            self.set_state_adding_cursor(False)

    def set_x_axis_title(self, title: str, label: str = None) -> None:
        """
        :param title: title for horizontal X axis;
        :param label: short name for horizontal X axis.
        """

        self._x_title = title
        self._x_label = label if label is not None else self._x_label
        self._set_axis_titles()

    def set_y_axis_title(self, title: str, label: str = None) -> None:
        """
        :param title: title for vertical Y axis;
        :param label: short name for vertical Y axis.
        """

        self._y_title = title
        self._y_label = label if label is not None else self._y_label
        self._set_axis_titles()

    @pyqtSlot(QPoint)
    def show_context_menu(self, pos: QPoint) -> None:
        """
        Slot shows context menu.
        :param pos: position of the context menu event that the widget receives.
        """

        if self._center_text_marker:
            return

        non_empty_curves = self.check_non_empty_curves()
        menu = QMenu(self)
        media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
        action_save_image = QAction(QIcon(os.path.join(media_dir, "save_image.png")),
                                    self._get_item_label("save_screenshot"), menu)
        action_save_image.setEnabled(non_empty_curves)
        action_save_image.triggered.connect(self.save_image)
        menu.addAction(action_save_image)
        action_export_ivc = QAction(QIcon(os.path.join(media_dir, "export.png")), self._get_item_label("export_ivc"),
                                    menu)
        action_export_ivc.setEnabled(non_empty_curves)
        action_export_ivc.triggered.connect(self.export_ivc)
        menu.addAction(action_export_ivc)
        if self._context_menu_works_with_cursors:
            action_add_cursor = QAction(QIcon(os.path.join(media_dir, "add_cursor.png")),
                                        self._get_item_label("add_cursor"), menu)
            action_add_cursor.triggered.connect(partial(self.add_cursor, pos))
            menu.addAction(action_add_cursor)
            if not self.cursors.is_empty():
                if self.cursors.find_cursor_for_context_menu(pos):
                    action_remove_cursor = QAction(QIcon(os.path.join(media_dir, "remove_cursor.png")),
                                                   self._get_item_label("remove_cursor"), menu)
                    action_remove_cursor.triggered.connect(self.remove_cursor)
                    menu.addAction(action_remove_cursor)
                action_remove_all_cursors = QAction(QIcon(os.path.join(media_dir, "remove_all_cursors.png")),
                                                    self._get_item_label("remove_all_cursors"), menu)
                action_remove_all_cursors.triggered.connect(self.remove_all_cursors)
                menu.addAction(action_remove_all_cursors)
        menu.popup(self.mapToGlobal(pos))

    def show_legend(self, legend_font: QFont = None) -> None:
        """
        Method displays legend for curves in plot.
        :param legend_font: font for legend.
        """

        legend = QwtLegend()
        if isinstance(legend_font, QFont):
            legend.setFont(legend_font)
        self.insertLegend(legend, QwtPlot.TopLegend)
