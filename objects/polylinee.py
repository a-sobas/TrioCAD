from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *

import heapq
from config.enums import Line_Pos
from config.enums import Item_Type
from objects.line import Line
from objects.line import Line_Pos
from .handles.handle import Handle
from objects.arc import Arc
import config.preferences as preferences


class Polyline(QGraphicsItem):

    count = 0

    def __init__(self, *points, is_closed=False):
        super(Polyline, self).__init__()

        self.type = Item_Type.Polyline
        self.index = Polyline.count
        Polyline.count = Polyline.count + 1

        self.is_painted = False

        self.points = []
        self.lines = []

        self.radii = []
        self.arcs = []
        self.previous_layer_arc = None
        self.next_layer_arc = None

        self.points.append(points[0])

        for i, point in enumerate(points):
            if i == 0:
                continue
            self.add_point(point)

        self.earlier_path = None

        self.init_flags()
        self.setAcceptHoverEvents(True)

        if is_closed:
            self.is_closed = True
            self.close_polyline()
        else:
            self.is_closed = False


    @property
    def p_num(self):
        return len(self.points)


    def add_point(self, point):

        self.points.append(point)
        self.create_line(self.points[-2], point)

        if self.p_num == 2:
            self.lines[-1].line_pos = Line_Pos.Lonely
        elif self.p_num == 3:
            self.lines[-2].line_pos = Line_Pos.First
            self.lines[-1].line_pos = Line_Pos.Last
        elif self.p_num >= 3:
            self.lines[-2].line_pos = Line_Pos.Between
            self.lines[-1].line_pos = Line_Pos.Last


    def create_line(self, p1, p2, line_index=None):
        if line_index is not None:
            index = line_index
        else:
            index = self.p_num-2

        self.lines.append(Line(p1, p2, index))
        self.lines[-1].setParentItem(self)


    def set_point(self, new_point):
        self.points[-1] = new_point
        self.lines[-1].set_p2(new_point)

        if self.arcs:
            self.update_arc(self.p_num - 3)   

        if self.lines[0].is_first_in_scene() and self.p_num == 2:
            self.scene().previous_layer_arc.update_line_2(self.lines[-1].line)         


    def create_prev_layer_arc(self, line_1, line_2, radius):
        if self.previous_layer_arc is not None:
            self.previous_layer_arc.setParentItem(None)
            self.scene().removeItem(self.previous_layer_arc)
            self.previous_layer_arc = None
        
        self.previous_layer_arc = Arc(
            radius,
            line_1,
            line_2,
            0
        )
        
        self.previous_layer_arc.setParentItem(self)
        

    def create_next_layer_arc(self, line_1, line_2, radius):
        if self.next_layer_arc is not None:
            self.next_layer_arc.setParentItem(None)
            self.scene().removeItem(self.next_layer_arc)
            self.next_layer_arc = None
    
        self.next_layer_arc = Arc(
            radius,
            line_1,
            line_2,
            0
        )

        self.next_layer_arc.setParentItem(self)
        

    def set_point_i(self, new_point, index):
        if (index == 0 or index == self.p_num-1) and self.is_closed:
            self.points[0] = new_point
            self.lines[0].set_p1(new_point)
            self.points[-1] = new_point
            self.lines[-1].set_p2(new_point)
        elif index == 0:
            self.points[0] = new_point
            self.lines[0].set_p1(new_point)
        elif index == self.p_num-1:
            self.points[-1] = new_point
            self.lines[-1].set_p1(new_point)
        else:
            self.points[index-1] = new_point
            self.lines[index-1].set_p2(new_point)
            self.points[index] = new_point
            self.lines[index].set_p1(new_point)
    
        self.update_arc(index)   
        self.update_arc(index + 1)   
        self.update_arc(index + 2)   


    def create_arc(self, r=None):
        
        if r is None:
            radius = preferences.default_radius
        else:
            radius = r 

        if self.p_num >= 3:
            self.arcs.append(
                    Arc(
                        radius,
                        self.lines[-2].line,
                        self.lines[-1].line,
                        self.p_num - 3
                    )
                )
            
            self.arcs[-1].setParentItem(self)        


    def create_arcs(self, *radii):
        for i, radius in enumerate(radii):
            if self.p_num >= 3:
                self.arcs.append(
                        Arc(
                            radius,
                            self.lines[i].line,
                            self.lines[i+1].line,
                            i
                        )
                    )
                
                self.arcs[-1].setParentItem(self) 
    
    
    def remove_arcs(self):
        for arc in self.arcs:
            self.scene().removeItem(arc)

        self.arcs = []


    def change_arc(self, i, r):
        arcs_num = len(self.arcs)

        if arcs_num and (i < arcs_num and i >= 0):
            self.arcs[i].set_radius(r)


    def update_arc(self, i):
        arcs_num = len(self.arcs)

        if arcs_num and (i < arcs_num and i >= 0):
            self.arcs[i].update()


    def remove_last_point(self):
        self.points.pop()
        self.scene().removeItem(self.lines[self.p_num-1])
        self.lines.pop()
        self.lines[-1].line_pos = Line_Pos.Last

        if len(self.lines) == 1:
            self.lines[0].line_pos = Line_Pos.Lonely


    def remove_last_arc(self):
        self.scene().removeItem(self.arcs[-1])
        self.arcs.pop()


    def init_flags(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)


    def add(self, *pol_points):
        for i in range(1, len(pol_points)):
            self.add_point(pol_points[i])


    def close_polyline(self):
        self.is_closed = True
        self.add_point(self.points[0])


    def close(self):
        self.is_closed = True


    def separate(self):
        self.is_closed = False
        self.scene().update()


    def mousePressEvent(self, e):
        e.ignore()
        super().mousePressEvent(e)


    def mouseMoveEvent(self, e):
        pos = e.pos()
        pos = self.mapToScene(pos)
        self.scene().parent().parentWidget().show_message(
            str(int(1000 * pos.x()) / 1000),  
            str(-int(1000 * pos.y()) / 1000)
        )

        e.ignore()
        super().mouseMoveEvent(e)


    def mouseReleaseEvent(self, e):
        e.ignore()
        super().mouseReleaseEvent(e)


    def hoverMoveEvent(self, e):
        e.ignore()
        super().hoverMoveEvent(e)


    def hoverLeaveEvent(self, e):
        e.ignore()
        super().hoverLeaveEvent(e)


    def create_earlier_path(self):
        path = QPainterPath()
        for line in self.lines:
            path.addPath(line.shape())

        self.earlier_path = path


    def delete_earlier_path(self):
        self.earlier_path = None


    def boundingRect(self):
        s = Handle.size / 2

        x_min = heapq.nsmallest(1, self.points, key=lambda p: p.x())[0].x()
        y_min = heapq.nsmallest(1, self.points, key=lambda p: p.y())[0].y()
        x_max = heapq.nlargest(1, self.points, key=lambda p: p.x())[0].x()
        y_max = heapq.nlargest(1, self.points, key=lambda p: p.y())[0].y()

        x = x_min
        y = y_min
        width = x_max - x_min
        height = y_max - y_min

        return QRectF(x, y, width, height).adjusted(-s, -s, s, s)


    def shape(self):
        path = QPainterPath()
        for child_item in self.childItems():
            path.addPath(child_item.shape())

        return path


    def paint(self, painter, option, widget=None):
        if self.earlier_path:
            painter.setPen(QPen(Qt.red, Handle.size / 3.0))
            painter.drawPath(self.earlier_path)