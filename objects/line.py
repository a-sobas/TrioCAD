from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *

import config.preferences as preferences
from .handles.handle import Handle
from .handles.linestarthandle import LineStartHandle
from .handles.lineendhandle import LineEndHandle
from .handles.linecenterhandle import LineCenterHandle
from .handles.lineconnecthandle import LineConnectHandle
from config.enums import Line_Pos
from config.enums import Item_Type
from config.enums import Item_Mode


class Line(QGraphicsItem):

    orange = QColor(qRgb(255, 140, 0))
    gray = QColor(qRgb(200, 200, 200))

    pen = QPen(Qt.black, 0.0, Qt.SolidLine)
    hover_brush = QBrush(orange)

    count = 0

    mode = Item_Mode.Creating

    def __init__(self, p1, p2, index, line_pos=Line_Pos.Between):
        """
        Initialize the shape.
        """
        super(Line, self).__init__()
        self.type = Item_Type.Line

        self.index = index

        if index == 0:
            self.line_pos = Line_Pos.First
        else:
            self.line_pos = line_pos

        self.is_painted = False

        self.points = [p1, p2]
        self.line = QLineF(p1, p2)
        self.real_line = None

        self.line_handles = {}
        self.line_center_handle = None

        self.press_pos = None
        self.move_pos = None
        self.move_pos_scene = None

        self.init_flags()
        self.setAcceptHoverEvents(True)

        self.is_painted = True

    def is_last_in_scene(self, rect=None):
        if self.scene() and self.scene().next_layer_anchor is not None and self.scene().next_layer_anchor.boundingRect().contains(self.line.p2()):
            return True
        elif rect and rect.contains(self.line.p2()):
            return True
        else:
            return False

    def is_first_in_scene(self, rect=None):
        if self.scene() and self.scene().previous_layer_anchor is not None and self.scene().previous_layer_anchor.boundingRect().contains(self.line.p1()):
            return True
        elif rect and rect.contains(self.line.p1()):
            return True
        else:
            return False

    def set_p1(self, new_point):
        self.points[0] = new_point
        self.line.setP1(new_point)

        self.parentItem().points[self.index] = new_point

        self.update()

    def set_p2(self, new_point):
        self.points[1] = new_point
        self.line.setP2(new_point)

        self.parentItem().points[self.index+1] = new_point

        self.update()

    def set_point(self, index, new_point, iteration=0):
        if iteration < 2:
            iteration = iteration + 1

            if index == 0:
                self.set_p1(new_point)
            else:
                self.set_p2(new_point)

        self.update()

    def set_line_center(self, new_center):
        offset = new_center - self.line.center()

        self.set_p1(self.points[0] + offset)
        self.set_p2(self.points[1] + offset)

    def init_flags(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

    def mousePressEvent(self, e):
        e.ignore()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        pos = e.pos()
        pos = self.mapToScene(pos)
        self.parent().parentWidget().show_message(
            str(int(1000 * pos.x()) / 1000), 
            str(-int(1000 * pos.y()) / 1000)
        )

        super().mouseMoveEvent(e)
        e.ignore()

    def mouseReleaseEvent(self, e):
        e.ignore()
        super().mouseReleaseEvent(e)

    def hoverMoveEvent(self, e):
        e.ignore()
        super().hoverMoveEvent(e)

    def hoverLeaveEvent(self, e):
        e.ignore()
        super().hoverLeaveEvent(e)

    def create_handles(self):
        if self.parentItem().is_closed and self.line_pos == Line_Pos.First:
            self.line_handles[0] = LineConnectHandle(
                self.points[0], self.index)
            self.line_handles[1] = LineEndHandle(self.points[1], self.index)
        elif self.parentItem().is_closed and self.line_pos == Line_Pos.Last:
            self.line_handles[0] = LineStartHandle(self.points[0], self.index)
            self.line_handles[1] = LineConnectHandle(
                self.points[1], self.index)
        else:
            self.line_handles[0] = LineStartHandle(self.points[0], self.index)
            self.line_handles[1] = LineEndHandle(self.points[1], self.index)

        self.line_handles[0].setParentItem(self)
        self.line_handles[1].setParentItem(self)

        self.line_center_handles = LineCenterHandle(
            self.line.center(),
            self.index
        )
        self.line_center_handles.setParentItem(self)

    def update_handles_pos(self):
        self.line_handles.clear()
        for childItem in self.childItems():
            childItem.remove()

        self.create_handles()

    def create_earlier_path(self):
        self.parentItem().create_earlier_path()

    def delete_earlier_path(self):
        self.parentItem().delete_earlier_path()

    def boundingRect(self):
        s = Handle.size / 2

        return QRectF(self.line.p1(), self.line.p2()).adjusted(-s, s, s, -s)

    def shape(self):

        path = QPainterPath()
        path.moveTo(self.points[0])
        path.lineTo(self.points[1])

        return path

    def paint(self, painter, option, widget=None):
        if Line.mode == Item_Mode.Creating:
            if not self.line_handles and self.isSelected():
                self.create_handles()
            elif self.line_handles and not self.isSelected():
                self.line_handles.clear()
                for childItem in self.childItems():
                    childItem.remove()

            painter.setRenderHint(QPainter.HighQualityAntialiasing)
        
        self.draw(painter, False)
        
    def draw(self, painter, is_background):


        if not is_background and self.mode == Item_Mode.Creating:
            if self.isSelected():
                painter.setPen(QPen(Qt.blue, preferences.size_factor / 3.0, Qt.SolidLine))
            else:    
                painter.setPen(QPen(Qt.black, preferences.size_factor / 3.0, Qt.SolidLine))
        elif not is_background and self.mode == Item_Mode.Showing:
            painter.setPen(QPen(Qt.black, preferences.size_factor / 2.5, Qt.SolidLine))
        elif is_background and self.mode == Item_Mode.Creating:
            painter.setPen(QPen(Line.gray, preferences.size_factor / 3.0, Qt.SolidLine))
        elif is_background and self.mode == Item_Mode.Showing:
            painter.setPen(QPen(Line.gray, preferences.size_factor / 2.5, Qt.SolidLine))

        self.create_real_line()

        if Line.mode == Item_Mode.Creating:
            self.draw_line(painter)
        elif Line.mode == Item_Mode.Showing:
            self.draw_line_s(painter)
            self.draw_arrow(painter)

    def draw_line(self, painter):
        painter.drawPath(self.shape())

    def create_real_line(self):
        if self.parentItem().arcs:
            p1 = QPointF()
            p2 = QPointF()
            if self.line_pos == Line_Pos.Lonely:
                p1 = self.line.p1()
                p2 = self.line.p2()
            elif self.line_pos == Line_Pos.First:
                p1 = self.line.p1()
                arc = self.parentItem().arcs[self.index]
                if arc.r != 0:
                    p2 = self.parentItem().arcs[self.index].points[0]
                else:
                    p2 = self.line.p2()
            elif self.line_pos == Line_Pos.Last:
                arc = self.parentItem().arcs[self.index-1]
                if arc.r != 0:
                    p1 = self.parentItem().arcs[self.index-1].points[1]
                else:
                    p1 = self.line.p1()
                p2 = self.line.p2()
            elif self.line_pos == Line_Pos.Between:
                arc = self.parentItem().arcs[self.index-1]
                if arc.r != 0:
                    p1 = self.parentItem().arcs[self.index-1].points[1]
                else:
                    p1 = self.line.p1()
                    
                arc = self.parentItem().arcs[self.index]
                if arc.r != 0:
                    p2 = self.parentItem().arcs[self.index].points[0]
                else:
                    p2 = self.line.p2()

            self.real_line = QLineF(p1, p2)
        else:
            self.real_line = self.line

        return self.real_line 

    def draw_line_s(self, painter):
        self.create_real_line()

        painter.drawLine(self.real_line)
        

    def draw_arrow(self, painter):
        line = QLineF(self.real_line.center(), QPointF())
        line.setLength(preferences.size_factor)
        line.setAngle(self.line.angle() - 210)
        painter.drawLine(line)
        line.setAngle(self.line.angle() - 150)
        painter.drawLine(line)