from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .handle import Handle
from .linehandle import LineHandle
from config.enums import Line_Pos


class LineConnectHandle(LineHandle):
    def __init__(self, pos, index):
        super(LineConnectHandle, self).__init__(pos, index)

        self.split = False


    def set_point(self, point, update=True):
        self.mouse_pos = point

        parent = self.parentItem()
        lines = parent.parentItem().lines

        if parent.line_pos == Line_Pos.First:
            parent.set_p1(self.mouse_pos)

            if lines[-1].isSelected():
                lines[-1].set_p2(self.mouse_pos)
                lines[-1].update_handles_pos()
            elif not self.split:
                self.split = True

        elif parent.line_pos == Line_Pos.Last:
            parent.set_p2(self.mouse_pos)

            if lines[0].isSelected():
                lines[0].set_p1(self.mouse_pos)
                lines[0].update_handles_pos()
            elif not self.split:
                self.split = True

        if update:
            parent.update_handles_pos()


    def release(self):
        if self.split:
            Handle.draw_handle = True
            self.parentItem().parentItem().separate()

            return True
        else:
            self.split = False

            return False


    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        if Handle.draw_handle:
            painter.setPen(self.drawing_pen)
            painter.setBrush(Qt.green)
            painter.drawPath(self.shape())
        else:
            pass