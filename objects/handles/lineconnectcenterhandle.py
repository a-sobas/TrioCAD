from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.RectF import RectF
from handles.handle import Handle
from handles.linehandle import LineHandle
from config.enums import Line_Pos


class LineConnectCenterHandle(LineHandle):
    def __init__(self, pos, index):
        super(LineConnectCenterHandle, self).__init__(pos, index)
        self.split_point_index = None
        self.separate = False


    def set_point(self, point, update=True):
        self.mouse_pos = point

        parent = self.parentItem()
        lines = parent.parentItem().lines

        parent.set_line_center(self.mouse_pos)

        if parent.line_pos == Line_Pos.Last:
            if lines[-2].isSelected():
                lines[-2].set_p2(parent.points[0])
                lines[-2].update_handles_pos()

            elif self.split_point_index is None:
                self.split_point_index = self.index

            if lines[0].isSelected():
                lines[0].set_p1(parent.points[1])
                lines[0].update_handles_pos()

            else:
                self.separate = True

        if parent.line_pos == Line_Pos.First:
            if lines[1].isSelected():
                lines[1].set_p1(parent.points[1])
                lines[1].update_handles_pos()

            elif self.split_point_index is None:
                self.split_point_index = self.index + 1

            if lines[-1].isSelected():
                lines[-1].set_p2(parent.points[0])
                lines[-1].update_handles_pos()

            else:
                self.separate = True

        if update:
            parent.update_handles_pos()


    def release(self):
        if self.separate:
            self.parentItem().parentItem().separate()

        Handle.draw_handle = True
        if self.split_point_index:
            self.scene().split_polyline(
                self.parentItem().parentItem().index,
                self.split_point_index
            )

            return True
        else:
            self.split_point_index = None

            return False


    def shape(self):
        s = Handle.size

        path = QPainterPath()
        path.addEllipse(RectF.rect_from_center(self.pos, s, s))
        return path


    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        if Handle.draw_handle:
            painter.setPen(self.drawing_pen)
            painter.setBrush(Qt.green)
            painter.drawPath(self.shape())
        else:
            pass