from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *

import math

import objects.utils.geometry as geometry
from utils.RectF import RectF
from config.enums import Item_Type
from config.enums import Item_Mode
import config.preferences as preferences
from .handles.handle import Handle


class Arc(QGraphicsItem):

    orange = QColor(qRgb(255, 140, 0))
    gray = QColor(qRgb(200, 200, 200))

    pen = QPen(Qt.black, 3.0, Qt.SolidLine)
    hover_brush = QBrush(orange)

    count = 0

    mode = Item_Mode.Creating

    def __init__(self, r, line_1, line_2, index):
        super(Arc, self).__init__()
        self.type = Item_Type.Arc
        self.index = index

        self.r = r
        
        self.line_1 = QLineF(line_1.p1(), line_1.p2())
        self.line_2 = QLineF(line_2.p1(), line_2.p2())

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)

        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

    def set_radius(self, r):
        self.r = r

        self.update()

        self.arc_status()

    def set_r(self, r):
        self.r = r

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def up(self):
        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def update(self):
        line_1 = self.parentItem().lines[self.index].line
        line_2 = self.parentItem().lines[self.index + 1].line
        self.line_1 = QLineF(line_1.p1(), line_1.p2())
        self.line_2 = QLineF(line_2.p1(), line_2.p2())

        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def update_12(self, new_line_1, new_line_2):
        self.line_1 = QLineF(new_line_1.p1(), new_line_1.p2())
        self.line_2 = QLineF(new_line_2.p1(), new_line_2.p2())

        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def update_line_2(self, new_line_2):
        self.line_2 = QLineF(new_line_2.p1(), new_line_2.p2())

        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def update_line_1(self, new_line_1):
        self.line_1 = QLineF(new_line_1.p1(), new_line_1.p2())

        if self.line_1.length() == 0 or self.line_2.length() == 0:
            self.drawing = False
        else:
            self.drawing = True

        points = geometry.calculate_characteristic_arc_parameters(
            self.r,
            self.line_1,
            self.line_2
        )

        self.arc_center, self.points = points[0], points[1:3]

        self.arc_status()

    def arc_status(self):
        try:
            parent = self.scene().views()[0].parent().parentWidget()
            m = parent.statusBar().currentMessage()
            if self.is_arc_possible() and (m == 'Arc is not valid' or m == ''):
                parent.statusBar().clearMessage()
            else:
                parent.show_info('Arc is not valid')
        except:
            pass

    def create_earlier_path(self):
        pass

    def delete_earlier_path(self):
        pass

    def boundingRect(self):
        return RectF.rect_from_center(self.arc_center, 2*self.r, 2*self.r)

    def shape(self):
        self.calculate_angles()

        path = QPainterPath()
        path.moveTo(self.points[0])
        path.arcTo(self.boundingRect(), self.start_angle, self.span_angle)
        
        return path

    def paint(self, painter, option, widget=None):
        if self.drawing:
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            if self.r != 0:
                painter.setPen(QPen(Qt.black, 0.0, Qt.SolidLine))

                s = preferences.size_factor / 3
                painter.setBrush(Qt.red)
                painter.drawLine(QLineF(
                    self.arc_center + QPointF(s, 0), 
                    self.arc_center + QPointF(-s, 0)
                ))
                painter.drawLine(QLineF(
                    self.arc_center + QPointF(0, s), 
                    self.arc_center + QPointF(0, -s)
                    ))
                painter.drawEllipse(RectF.rect_from_center(self.arc_center, s / 2, s / 2))
                
                self.draw(painter, False)

    def is_arc_possible(self):
        if self.r == 0:
            return True

        try:
            parent = self.parentItem()
            if parent and self.index + 1 < len(parent.lines):

                line_1 = parent.lines[self.index]
                line_2 = parent.lines[self.index + 1]
                line_1.create_real_line()
                line_2.create_real_line()

                if math.fabs(line_1.line.angle() - line_1.real_line.angle()) > 1:
                    return False
                elif math.fabs(line_2.line.angle() - line_2.real_line.angle()) > 1:
                    return False
                else:
                    return True
            else:
                return True
        except:
            return True

    def calculate_angles(self):
        self.start_angle = QLineF(self.arc_center, self.points[0]).angle()
        self.span_angle = QLineF(
            self.arc_center,
            self.points[1]
        ).angle() - self.start_angle

        if math.fabs(self.span_angle) < 180:
            pass
        elif self.span_angle < 0:
            self.span_angle = 360 + self.span_angle
        elif self.span_angle > 0:
            self.span_angle = self.span_angle - 360

    def draw_arc(self, painter):
    
        self.calculate_angles()
        
        painter.drawArc(
            self.boundingRect(),
            self.start_angle*16,
            self.span_angle*16
         )
        
        if not self.is_arc_possible():
            painter.setPen(QPen(Qt.red, 0.0, Qt.DashDotDotLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(
                self.parentItem().points[self.index+1], 
                preferences.size_factor * 5, 
                preferences.size_factor * 5
            )
        

    def draw(self, painter, is_background):
        if not is_background and Arc.mode == Item_Mode.Creating:
            painter.setPen(QPen(Qt.black, 0.0, Qt.DashDotDotLine))
        elif not is_background and Arc.mode == Item_Mode.Showing:
            painter.setPen(QPen(Qt.black, Handle.size / 2.5, Qt.SolidLine))
        elif is_background and Arc.mode == Item_Mode.Creating:
            painter.setPen(QPen(Arc.gray, 0.0, Qt.DashDotDotLine))
        elif is_background and Arc.mode == Item_Mode.Showing:
            painter.setPen(QPen(Arc.gray, Handle.size / 4.0, Qt.SolidLine))

        self.draw_arc(painter)
