from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .handle import Handle
from .linehandle import LineHandle
from config.enums import Line_Pos


class LineEndHandle(LineHandle):
    def __init__(self, pos, index):
        super(LineEndHandle, self).__init__(pos, index)

        self.split_point_index = None

        self.move_anchor = False


    def mousePressEvent(self, e):
        if self.parentItem().is_last_in_scene():
            self.move_anchor = True
        
        super().mousePressEvent(e)


    def set_point(self, point, update=True):
        self.mouse_pos = point

        parent = self.parentItem()
        p_parent = parent.parentItem()

        lines = p_parent.lines

        parent.set_p2(self.mouse_pos)
        parent.parentItem().update_arc(self.index-1)
        
        if self.move_anchor:
            print('a')
            self.scene().next_scene().first_polyline().lines[0].set_p1(self.mouse_pos)
            self.scene().next_layer_anchor.pos = self.mouse_pos
            self.scene().next_scene().previous_layer_anchor.pos = self.mouse_pos

            r = self.scene().next_layer_arc.r
            self.scene().create_layer_arcs_ending(p_parent, r)

        if parent.line_pos == Line_Pos.First or parent.line_pos == Line_Pos.Between:
            if lines[self.index+1].isSelected():
                self.split_point_index = None

                lines[self.index+1].set_p1(self.mouse_pos)
                p_parent.update_arc(self.index)
                p_parent.update_arc(self.index + 1)

            elif self.split_point_index is None:
                p_parent.arcs[self.index].set_r(0)
                self.split_point_index = self.index + 1

        if update:
            parent.update_handles_pos()


    def release(self):
        if self.split_point_index is not None:
            Handle.draw_handle = True
            self.scene().split_polyline(
                self.parentItem().parentItem().index,
                self.split_point_index
            )

            return True
        else:
            parent = self.parentItem()
            p_parent = parent.parentItem()
            if parent.line_pos == Line_Pos.First or parent.line_pos == Line_Pos.Between:
                p_parent.lines[self.index+1].update_handles_pos()
            self.split_point_index = None

            return False


    def get_coordinates(self):
        super().get_coordinates()

        r = self.str_to_float(self.w.edit_r.text())
        if r is not None:
            p_parent = self.parentItem().parentItem()
            if p_parent.arcs:
                p_parent.change_arc(self.index, r)
            if self.scene().next_layer_arc:
                self.scene().next_layer_arc.set_r(r)

        if self.scene():
            self.scene().update()


    def paint(self, painter, option, widget=None):
        if self.draw_coordinates:
                painter.setPen(QPen(Qt.black, 0.0, Qt.SolidLine))
                
                font = painter.font()
                font.setPixelSize(Handle.size * 1.4) 
                font.setWeight(QFont.Thin)
                painter.setFont(font)

                
                text_x = 'X: ' + str(int(self.pos.x()*100) / 100)
                text_y = 'Y: ' + str(int(-self.pos.y()*100) / 100)

                if self.index < (self.parentItem().parentItem().p_num - 2):
                    text_r = 'R: ' +  str(self.parentItem().parentItem().arcs[self.index - 1].r)
                    text = text_r + '  ' + text_x + '  ' + text_y
                else:
                    text = text_x + '  ' + text_y
                painter.drawText(self.pos + QPointF(10, -10), text)

        super().paint(painter, option, widget)