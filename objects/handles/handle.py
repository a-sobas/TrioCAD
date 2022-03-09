from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.RectF import RectF
import config.preferences as preferences


class Handle(QGraphicsItem):

    size = preferences.size_factor

    # flag which depends when handles are drawn
    draw_handle = True


    def __init__(self, pos, index):

        super(Handle, self).__init__()

        self.pos = pos
        self.index = index  # index of corresponding point

        self.drawing_pen = None
        self.drawing_brush = None

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)

        self.draw_coordinates = False


    def remove(self):
        self.scene().removeItem(self)


    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        if e.button() == Qt.LeftButton:
            Handle.draw_handle = False
            if self.parentItem() is not None:
                self.parentItem().create_earlier_path()


    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        if e.button() == Qt.LeftButton:

            Handle.draw_handle = True
            if self.parentItem() is not None:
                self.parentItem().delete_earlier_path()
        else:
            pass


    def release(self):
        pass


    def boundingRect(self):
        s = Handle.size

        return RectF.rect_from_center(self.pos, s, s)


    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        if Handle.draw_handle:
            painter.setPen(self.drawing_pen)
            painter.setBrush(self.drawing_brush)
            painter.drawPath(self.shape())
        else:
            pass
