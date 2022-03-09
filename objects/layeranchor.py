from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.RectF import RectF
import config.preferences as pref

class LayerAnchor(QGraphicsItem):

    pen = QPen(Qt.green, 0.0, Qt.SolidLine)
    hover_pen = QPen(QColor(qRgb(255, 140, 0)), 0.0, Qt.SolidLine)

    brush = Qt.green
    hover_brush = QColor(qRgb(255, 140, 0))

    def __init__(self, pos, ):
        super(LayerAnchor, self).__init__()

        self.pos = pos

        self.drawing_pen = LayerAnchor.pen
        self.drawing_brush = LayerAnchor.brush

        self.setAcceptHoverEvents(True)

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)


    def hoverMoveEvent(self, e):
        self.drawing_pen = LayerAnchor.hover_pen
        self.drawing_brush = LayerAnchor.hover_brush

        self.draw_coordinates = True
        super().hoverMoveEvent(e)

    def hoverLeaveEvent(self, e):
        self.drawing_pen = LayerAnchor.pen
        self.drawing_brush = LayerAnchor.brush

        self.draw_coordinates = False
        super().hoverLeaveEvent(e)

    def boundingRect(self):
        return RectF.rect_from_center(self.pos, pref.size_factor, pref.size_factor)

    def shape(self):
        offset = pref.size_factor / 2
        p1, p3 = self.pos + QPointF(-offset, 0), self.pos + QPointF(offset, 0)
        p2, p4 = self.pos + QPointF(0, -offset), self.pos + QPointF(0, offset)

        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p4)
        path.lineTo(p1)
        return path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.drawing_pen)
        painter.setBrush(self.drawing_brush)

        offset = pref.size_factor / 2
        p1, p3 = self.pos + QPointF(-offset, 0), self.pos + QPointF(offset, 0)
        p2, p4 = self.pos + QPointF(0, -offset), self.pos + QPointF(0, offset)

        painter.drawConvexPolygon(p1, p2, p3, p4)