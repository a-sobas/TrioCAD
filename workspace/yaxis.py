from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *


class YAxis(QGraphicsScene):
    def __init__(self, parent=None):
        super(YAxis, self).__init__(parent)
        self.y_dists = None
        self.y_texts = None


    def drawBackground(self, painter, rect):
        if self.y_dists:
            for dist in self.y_dists:
                painter.drawLine(-6, dist, -1, dist)

            font = painter.font()
            font.setPixelSize(11) 
            font.setWeight(QFont.Thin)
            painter.setFont(font)

            painter.rotate(270)
            
            # x w dol
            # y w lewo

            dist = 30
            text_rect = QRectF(QPointF(-15, -16), QPointF(15, -6))
            
            for dist, text in zip(self.y_dists, self.y_texts):
                dist, text = -dist, -text
                text_rect = QRectF(
                    QPointF(dist, - 16) + QPointF(- 15, 0), 
                    QPointF(dist, -16) + QPointF(15, 10)
                )
                painter.drawText(text_rect, Qt.AlignCenter, str(text));      