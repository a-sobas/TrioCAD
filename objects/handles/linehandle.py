from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.RectF import RectF
from .handle import Handle
from workspace.window import ChangePointRadiusWindow


class LineHandle(Handle):
    pen = QPen(Qt.darkRed, 0.0, Qt.SolidLine)
    hover_pen = QPen(QColor(qRgb(255, 140, 0)), 0.0, Qt.SolidLine)

    brush = Qt.red
    hover_brush = QColor(qRgb(255, 140, 0))


    def __init__(self, pos, index):
        super(LineHandle, self).__init__(pos, index)

        self.press_pos = None
        self.mouse_pos = None

        self.drawing_pen = LineHandle.pen
        self.drawing_brush = LineHandle.brush

        self.drawing_assistant = None
        self.near_point_found = False

        self.move = False
        self.splitted = False

        self.w = None


    def create_change_point_window(self):
        self.w = ChangePointRadiusWindow(self)
        self.w.set_button.clicked.connect(self.get_coordinates)

        view = self.scene().views()[0]
        point_scene = self.mapToScene(self.press_pos)
        point_view = view.mapFromScene(point_scene)
        point = view.viewport().mapToGlobal(point_view) + QPoint(10, 10)
        self.w.move(point)


    def get_coordinates(self):
        x = self.str_to_float(self.w.edit_x.text())
        y = self.str_to_float(self.w.edit_y.text())

        if x is not None and y is not None:
            self.w.close()
            self.set_point(QPointF(x, -y))
        else:
            pass


    def str_to_float(self, str):
        result = None
        try:
            result = float(str)
        except:
            pass

        return result


    def hoverMoveEvent(self, e):
        self.drawing_pen = LineHandle.hover_pen
        self.drawing_brush = LineHandle.hover_brush

        self.draw_coordinates = True
        super().hoverMoveEvent(e)


    def hoverLeaveEvent(self, e):
        self.drawing_pen = LineHandle.pen
        self.drawing_brush = LineHandle.brush

        self.draw_coordinates = False
        super().hoverLeaveEvent(e)


    def mousePressEvent(self, e):
        self.press_pos = e.scenePos()

        if e.button() == Qt.RightButton:
            self.move = False
            self.create_change_point_window()
            self.w.show()
        elif e.button() == Qt.LeftButton:
            self.move = True
            self.set_point(self.press_pos,  False)

        super().mousePressEvent(e)


    def mouseMoveEvent(self, e):
            if self.move:
                self.pos = e.pos()
                self.pos = self.mapToScene(self.pos)
                self.scene().parent.show_message(
                    str(int(1000 * self.pos.x()) / 1000), 
                    str(-int(1000 * self.pos.y()) / 1000)
                )
                self.mouse_pos = e.scenePos()
                self.set_point(self.mouse_pos, False)


    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:

            parent = self.parentItem()

            Handle.draw_handle = True
            if parent is not None:
                parent.delete_earlier_path()

                if not self.release():
                    parent.update_handles_pos()
        else:
            pass


    def set_point(self, point=None, update=True):
        pass


    def release(self):
        pass


    def shape(self):
        s = Handle.size

        path = QPainterPath()
        path.addRect(RectF.rect_from_center(self.pos, s, s))
        return path


    def paint(self, painter, option, widget=None):

        if self.press_pos and self.mouse_pos:
            painter.setPen(QPen(Qt.black, 0, Qt.DashDotDotLine))
            painter.drawLine(
                self.mapFromScene(self.mouse_pos),
                self.mapFromScene(self.press_pos)
            )

        if self.near_point_found:
            s = Handle.size

            painter.setPen(QPen(Qt.yellow, 4.0, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)

            painter.drawRect(RectF.rect_from_center(
                self.mapFromScene(self.mouse_pos), s, s)
            )

        super().paint(painter, option, widget)
