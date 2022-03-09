from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.RectF import RectF
from .handle import Handle
from .linehandle import LineHandle
from workspace.window import SetPointWindow
from config.enums import Line_Pos


class LineCenterHandle(LineHandle):
    pen = QPen(Qt.darkBlue, 0.0, Qt.SolidLine)
    hover_pen = QPen(QColor(qRgb(255, 140, 0)), 0.0, Qt.SolidLine)

    brush = Qt.blue
    hover_brush = QColor(qRgb(255, 140, 0))


    def __init__(self, pos, index):
        super(LineCenterHandle, self).__init__(pos, index)

        self.drawing_pen = LineCenterHandle.pen
        self.drawing_brush = LineCenterHandle.brush

        self.split_point_1_index = None
        self.split_point_2_index = None

        self.move = False

        self.move_anchor_start = False
        self.move_anchor_end = False
 
        self.w = None


    def hoverMoveEvent(self, e):
        self.drawing_pen = LineCenterHandle.hover_pen
        self.drawing_brush = LineCenterHandle.hover_brush
        self.draw_coordinates = True


    def hoverLeaveEvent(self, e):
        self.drawing_pen = LineCenterHandle.pen
        self.drawing_brush = LineCenterHandle.brush
        self.draw_coordinates = False


    def mousePressEvent(self, e):
        self.press_pos = e.scenePos()

        if e.button() == Qt.RightButton:
            self.move = False
            self.create_change_point_window()
            self.w.show()
        elif e.button() == Qt.LeftButton:
            self.move = True
            self.set_point(self.press_pos,  False)

        if self.parentItem().is_first_in_scene():
            self.move_anchor_start = True

        if self.parentItem().is_last_in_scene():
            self.move_anchor_end = True

        super().mousePressEvent(e)


    def create_change_point_window(self):
        self.w = SetPointWindow(self)
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


    def set_point(self, point, update=True):
        self.mouse_pos = point

        self.parentItem().set_line_center(self.mouse_pos)

        parent = self.parentItem()
        p_parent = parent.parentItem()
        lines = parent.parentItem().lines

        if self.move_anchor_start:
            print('b')
            self.scene().previous_scene().last_polyline().lines[-1].set_p2(self.mouse_pos)
            self.scene().previous_layer_anchor.pos = self.mouse_pos
            self.scene().previous_scene().next_layer_anchor.pos = self.mouse_pos

            self.scene().previous_layer_arc.update_12(
                self.scene().previous_scene().last_polyline().lines[-1].line, 
                lines[0].line
            )
            r = self.scene().previous_layer_arc.r
            self.scene().create_layer_arcs_starting(p_parent, r)
            
            if self.scene().previous_scene().last_polyline().arcs:
                self.scene().previous_scene().last_polyline().arcs[-1].update()

        if self.move_anchor_end:
            print('a')
            self.scene().next_scene().first_polyline().lines[0].set_p1(self.mouse_pos)
            self.scene().next_layer_anchor.pos = self.mouse_pos
            self.scene().next_scene().previous_layer_anchor.pos = self.mouse_pos

            r = self.scene().next_layer_arc.r
            self.scene().create_layer_arcs_ending(p_parent, r)

        if parent.line_pos == Line_Pos.Between or parent.line_pos == Line_Pos.Last:
            if lines[self.index-1].isSelected():
                lines[self.index-1].set_p2(parent.points[0])
                parent.parentItem().update_arc(self.index - 1)
                parent.parentItem().update_arc(self.index - 2)
            elif self.split_point_1_index is None:
                p_parent.arcs[self.index-1].set_r(0)
                self.split_point_1_index = self.index
        
        if parent.line_pos == Line_Pos.First or parent.line_pos == Line_Pos.Between:
            if lines[self.index+1].isSelected():
                lines[self.index+1].set_p1(parent.points[1])
                parent.parentItem().update_arc(self.index)
                parent.parentItem().update_arc(self.index + 1)
            elif self.split_point_2_index is None:
                p_parent.arcs[self.index].set_r(0)
                self.split_point_2_index = self.index + 1


    def release(self):
        split_points = []

        if self.split_point_1_index is not None:
            split_points.append(self.split_point_1_index)
        if self.split_point_2_index is not None:
            split_points.append(self.split_point_2_index)

        if len(split_points) == 1:
            Handle.draw_handle = True
            self.scene().split_polyline(
                self.parentItem().parentItem().index,
                *split_points
            )

            return True
        elif len(split_points) == 2:
            Handle.draw_handle = True
            self.scene().double_split_polyline(
                self.parentItem().parentItem().index,
                *split_points
            )

            return True
        else:
            parent= self.parentItem()
            lines = parent.parentItem().lines
            
            if parent.line_pos == Line_Pos.Between or parent.line_pos == Line_Pos.Last:
                lines[self.index-1].update_handles_pos()
            if parent.line_pos == Line_Pos.First or parent.line_pos == Line_Pos.Between:
                lines[self.index+1].update_handles_pos()
            
            if self.update:
                self.parentItem().update_handles_pos()

            self.split_point_index = None

            return False


    def shape(self):
        s = Handle.size

        path = QPainterPath()
        path.addEllipse(RectF.rect_from_center(self.pos, s, s))
        return path


    def paint(self, painter, option, widget=None):
        painter.setPen(LineCenterHandle.pen)
        if self.draw_coordinates:
            painter.setPen(QPen(Qt.black, 0.0, Qt.SolidLine))
                
            font = painter.font()
            font.setPixelSize(Handle.size * 1.4) 
            font.setWeight(QFont.Thin)
            painter.setFont(font)

            text = 'L: ' + str(int(1000 * self.parentItem().line.length()) / 1000)
            painter.drawText(self.pos + QPointF(10, -10), text)
    
        super().paint(painter, option, widget)
