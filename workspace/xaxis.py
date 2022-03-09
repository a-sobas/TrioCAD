from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

class XAxis(QGraphicsScene):

    def __init__(self, parent=None):
        super(XAxis, self).__init__(parent)
        self.x_dists = None
        self.x_texts = None

    def drawBackground(self, painter, rect):
        if self.x_dists:
            for dist in self.x_dists:
                painter.drawLine(dist, 0, dist, 5)

            font = painter.font()
            font.setPixelSize(11) 
            font.setWeight(QFont.Thin)
            painter.setFont(font)

            for dist, text in zip(self.x_dists, self.x_texts):
                text_rect = QRectF(
                    QPointF(dist, 6) + QPointF(- 30, 0), 
                    QPointF(dist, 6) + QPointF(30, 10)
                )
                painter.drawText(text_rect, Qt.AlignCenter, str(text))