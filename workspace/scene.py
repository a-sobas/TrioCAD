from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

import math
from enum import Enum

from .coursor import Coursor
from .drawingassistant import DrawingAssistant
from config.enums import Item_Type
from objects.polylinee import Polyline
from objects.arc import Arc
from .window import SetPointRadiusWindow
import config.preferences as preferences


class Mode(Enum):
    NoMode = 0,
    SelectObject = 1,
    DrawLine = 2


#-------------------------------------------------------#
#------------------ Scene CLASS ------------------------#
#-------------------------------------------------------#


class Scene(QGraphicsScene):

    # ------- __init__

    def __init__(self, parent=None, index=None):
        super(Scene, self).__init__(parent)
        self.sceneMode = Mode.NoMode

        self.name = None

        self.index = index

        self.is_active = True

        self.polylines = {}

        self.mouse_press = QPointF()
        self.mouse_move = QPointF()
        self.itemToDraw = 0

        self.mouse_presses = 0
        self.is_drawing = False

        self.drawing_assistant = DrawingAssistant()
        self.help_item = None
        self.help_line = None
        
        self.coursor = Coursor()
        
        self.item_to_remove = None

        self.parent = parent

        self.set_window = None

        self.previous_layer_anchor = None
        self.next_layer_anchor = None

        self.previous_layer_arc = None
        self.next_layer_arc = None


    def previous_scene(self):
        try:
            if self.index > 0:
                return self.views()[0].parentWidget().parentWidget().scenes[self.index - 1]
            else: 
                return -1
        except:
            return False


    def next_scene(self):
        try:
            if self.index < (len(self.views()[0].parentWidget().parentWidget().scenes.scenes) - 1):
                return self.views()[0].parentWidget().parentWidget().scenes[self.index + 1]
            else: 
                return -1
        except:
            return False


    def first_polyline(self): 
        for item in self.items():
            if isinstance(item, Polyline):
                if item.lines[0].is_first_in_scene():
                    return item
        return None
            

    def last_polyline(self): 
        for item in self.items():
            if isinstance(item, Polyline):
                if item.lines[-1].is_last_in_scene():
                    return item
        return None


# -------- setMode
    def setMode(self, mode):
        self.sceneMode = mode
        vMode = QGraphicsView.NoDrag
        if mode == Mode.DrawLine:
            self.update()
            self.makeItemsControllable(False)
            vMode = QGraphicsView.NoDrag
        elif mode == Mode.SelectObject:
            self.update()
            self.makeItemsControllable(True)
            vMode = QGraphicsView.RubberBandDrag

        mView = self.views()[0]

        if mView:
            mView.setDragMode(vMode)

    def set_active(self, is_active):
        self.is_active = is_active
            

# -------- mousePressEvent
    def mousePressEvent(self, e):
        if self.is_active:
            
            self.mouse_press = QPointF(
                int(e.scenePos().x() * 1000) / 1000, 
                int(e.scenePos().y() * 1000) / 1000
            )

            if self.sceneMode == Mode.DrawLine:
                if e.button() == Qt.LeftButton:
                    self.set_window = None
                    if self.previous_layer_anchor and self.previous_layer_anchor.boundingRect().contains(self.mouse_press):
                        self.mouse_press = self.previous_layer_anchor.pos
                        self.set_point() 
                        
                        self.create_layer_arcs_starting(self.itemToDraw, preferences.default_radius)
                        
                    elif self.next_layer_anchor and self.next_layer_anchor.boundingRect().contains(self.mouse_press):
                        self.mouse_press = self.next_layer_anchor.pos
                        self.set_point()
                        
                        self.create_layer_arcs_ending(self.itemToDraw, preferences.default_radius)
                        
                    elif self.drawing_assistant.n_point: 
                        self.mouse_press = self.drawing_assistant.n_point
                        self.set_point()
                    else:
                        self.set_point()

                if e.button() == Qt.RightButton:
                    self.set_window = SetPointRadiusWindow(self)
                    self.set_window.add_button.clicked.connect(self.get_coordinates)

                    view = self.views()[0]
                    point_view = view.mapFromScene(self.mouse_press)
                    point = view.viewport().mapToGlobal(point_view) + QPoint(10, 10)

                    self.set_window.move(point)
                    self.set_window.show()
                
            super().mousePressEvent(e)
            self.update()


    def create_layer_arcs_starting(self, polyline, starting_radius):
        item = polyline
        if self.previous_scene() != -1 and self.previous_scene() and self.previous_scene().last_polyline():
            l_1 = self.previous_scene().last_polyline().lines[-1].line
            l_2 = item.lines[0].line
            line_1 = QLineF(l_1.p1(), l_1.p2())
            line_2 = QLineF(l_2.p1(), l_2.p2())
            
            if self.previous_layer_arc is None:
                self.previous_layer_arc = Arc(starting_radius, line_1, line_2, polyline)    
                self.addItem(self.previous_layer_arc)
            else:
                self.previous_layer_arc.update_12(line_1, line_2)
                self.previous_layer_arc.set_r(starting_radius)
        elif not self.previous_scene():
            if self.first_polyline():
                l_1 = item.lines[-1].line
                l_2 = self.first_polyline().lines[0].line
                line_1 = QLineF(l_1.p1(), l_1.p2())
                line_2 = QLineF(
                    l_2.p1() + QPointF(0.001, 0.001) - QPointF(0.001, 0.001), 
                    l_2.p2() + QPointF(0.001, 0.001)- QPointF(0.001, 0.001)
                    )
                if self.previous_layer_arc is None:
                    self.previous_layer_arc = Arc(starting_radius, line_1, line_2, polyline.index)    
                    self.addItem(self.previous_layer_arc)
                else:
                    self.previous_layer_arc.update_12(line_1, line_2)
                    self.previous_layer_arc.set_r(starting_radius)
                      

    def create_layer_arcs_ending(self, polyline, ending_radius):
        item = polyline
        if self.next_scene() != -1 and self.next_scene() and self.next_scene().first_polyline():
            l_1 = item.lines[-1].line
            l_2 = self.next_scene().first_polyline().lines[0].line
            line_1 = QLineF(l_1.p1(), l_1.p2())
            line_2 = QLineF(l_2.p1(), l_2.p2())
        
            if self.next_layer_arc is None:
                self.next_layer_arc = Arc(ending_radius, line_1, line_2, polyline.index)
                self.addItem(self.next_layer_arc)
            else:
                self.next_layer_arc.update_12(line_1, line_2)
                self.next_layer_arc.set_r(ending_radius)
        elif not self.next_scene():
            if self.last_polyline():
                l_1 = self.last_polyline().lines[-1].line
                l_2 = item.lines[0].line
                line_1 = QLineF(l_1.p1(), l_1.p2())
                line_2 = QLineF(
                    l_2.p1() + QPointF(0.001, 0.001) - QPointF(0.001, 0.001), 
                    l_2.p2() + QPointF(0.001, 0.001)- QPointF(0.001, 0.001)
                    )
                if self.next_layer_arc is None:
                    self.next_layer_arc = Arc(ending_radius, line_1, line_2, polyline.index)
                    self.addItem(self.next_layer_arc)
                else:
                    self.next_layer_arc.update_12(line_1, line_2)
                    self.next_layer_arc.set_r(ending_radius)
  

    def remove_layer_arcs_starting(self):
        try:
            self.previous_layer_arc.set_r(0)
        except:
            pass


    def remove_layer_arcs_ending(self):
        try:
            self.next_layer_arc.set_r(0)
        except:
            pass


    def get_coordinates(self):
        r = self.str_to_float(self.set_window.edit_r.text())
        x = self.str_to_float(self.set_window.edit_x.text())
        y = self.str_to_float(self.set_window.edit_y.text())

        if x is not None and y is not None:
            self.mouse_press = QPointF(x, -y)
            self.set_point()
        else:
            pass

        if r is not None and self.itemToDraw.arcs:
            self.itemToDraw.change_arc(self.itemToDraw.arcs[-1].index, r)


    def str_to_float(self, s):
        result = None
        try:
            result = float(s)
        except:
            pass

        return result


    def set_point(self, point = None):
        if point:
            self.mouse_press = point

        self.drawing_assistant.mouse_press = self.mouse_press

        if not self.itemToDraw:
            if self.drawing_assistant.polyline_to_add is not None:
                self.itemToDraw = Polyline(*self.drawing_assistant.points_to_add)
                
                if self.drawing_assistant.polyline_to_add.previous_layer_arc:
                    self.create_layer_arcs_starting(
                        self.itemToDraw, 
                        self.drawing_assistant.polyline_to_add.previous_layer_arc.r
                    )
                    
                if self.drawing_assistant.polyline_to_add.next_layer_arc:
                    self.create_layer_arcs_ending(
                        self.itemToDraw, 
                        self.drawing_assistant.polyline_to_add.next_layer_arc.r
                    )
                    
                self.itemToDraw.add_point(self.drawing_assistant.points_to_add[-1])
                self.itemToDraw.create_arcs(*self.drawing_assistant.radii_to_add)
                self.remove_polyline(self.drawing_assistant.polyline_to_add.index)
            else:
                self.itemToDraw = Polyline(
                    self.mouse_press, 
                    self.mouse_press + QPointF(0.001, 0.001)
                )
            self.addItem(self.itemToDraw)
        else:
            self.itemToDraw.set_point(self.mouse_press)
            if self.drawing_assistant.polyline_to_add is not None:
                if self.drawing_assistant.polyline_to_add.index == self.itemToDraw.index:
                    pass
                else:
                    radii = []
                    for arc in self.itemToDraw.arcs:
                        radii.append(arc.r)
                    radii.extend(self.drawing_assistant.radii_to_add)
                    self.itemToDraw.add(*self.drawing_assistant.points_to_add)

                    if self.drawing_assistant.polyline_to_add.previous_layer_arc: 
                        self.create_layer_arcs_starting(
                            self.itemToDraw, 
                            self.drawing_assistant.polyline_to_add.previous_layer_arc.r
                        )
                        
                    if self.drawing_assistant.polyline_to_add.next_layer_arc:
                        self.create_layer_arcs_ending(
                            self.itemToDraw, 
                            self.drawing_assistant.polyline_to_add.next_layer_arc.r
                        )
                        
                    self.itemToDraw.arcs = []
                    self.itemToDraw.create_arcs(*radii)
                    self.remove_polyline(self.drawing_assistant.polyline_to_add.index)
                self.finish_drawing()
            else:
                self.itemToDraw.add_point(self.mouse_press + QPointF(0.01, 0.01))
                self.itemToDraw.create_arc()

        self.remove_help_items()


# ------- mouseMoveEvent
    def mouseMoveEvent(self, e):
        if self.is_active:
            pos = QPointF(int(e.scenePos().x()*1000) / 1000, int(e.scenePos().y()*1000) / 1000)
            self.coursor.set_pos(pos)

            if self.sceneMode != Mode.SelectObject and self.sceneMode != Mode.DrawLine:
                self.mouse_move = self.assist(
                    pos, 
                    self.coursor.covered_items(self.items()), 
                    preferences.grid_offset,
                    self.parent.attraction_to_point_action.isChecked(),
                    self.parent.orto_action.isChecked(),
                    self.parent.attraction_action.isChecked()
                )

            if self.sceneMode == Mode.DrawLine:
                if self.itemToDraw:
                    self.itemToDraw.set_point(
                        self.assist(
                            pos, 
                            self.coursor.covered_items(
                                self.items(),
                                self.itemToDraw.p_num-2,
                                self.itemToDraw.index
                            ),
                            preferences.grid_offset,
                            self.parent.attraction_to_point_action.isChecked(),
                            self.parent.orto_action.isChecked(),
                            self.parent.attraction_action.isChecked(),
                            True
                        )
                )
                else:
                    self.assist(
                        pos, 
                        self.coursor.covered_items(self.items()), 
                        preferences.grid_offset,
                        self.parent.attraction_to_point_action.isChecked(),
                        self.parent.orto_action.isChecked(),
                        self.parent.attraction_action.isChecked()
                        )

            super().mouseMoveEvent(e)
            self.update()


    # -------- mouseReleaseEvent
    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

    def assist(
        self, 
        actual_pos, 
        items, 
        offset, 
        attraction_to_point_action, 
        orto_action, 
        attraction_action,
        item_to_draw = False):
        
        pos = self.drawing_assistant.calculate_pos(
            actual_pos,
            items,
            item_to_draw,
            offset,
            attraction_to_point_action, 
            orto_action, 
            attraction_action
        )

        if not self.drawing_assistant.draw_item_flag or not self.drawing_assistant.help_line:
            self.remove_help_items()

        if self.drawing_assistant.draw_item_flag and not self.help_item:
            self.help_item = self.drawing_assistant.n_point_item
            self.addItem(self.help_item)
    
        if self.drawing_assistant.help_line and not self.help_line:
            if self.help_line:
                self.removeItem(self.help_line)
                self.help_line = 0
            self.help_line = self.drawing_assistant.help_line
            self.addItem(self.help_line)
        elif not self.drawing_assistant.help_line and self.help_line:
            self.removeItem(self.help_line)
            self.help_line = 0

        if self.help_item:
            self.help_item.setBrush(self.drawing_assistant.n_point_item_brush)
    
        return pos


# -------- keyPressEvent
    def keyPressEvent(self, e):
        if self.is_active:
            if e.key() == Qt.Key_Delete and self.sceneMode == Mode.SelectObject:
                self.remove_items()

            elif e.key() == Qt.Key_Escape and self.sceneMode == Mode.DrawLine:
                if self.itemToDraw:
                    if self.itemToDraw.p_num == 2:
                        # remove item when it represents only line
                        self.removeItem(self.itemToDraw)
                    else:
                        # remove last point when itemToDraw represents polyline
                        self.itemToDraw.remove_last_arc()
                        self.itemToDraw.remove_last_point()
                    if self.help_line:
                        self.removeItem(self.help_line)
                        self.help_line = 0

                self.finish_drawing()
            
            elif e.key() == Qt.Key_Escape:
                if self.itemToDraw:
                    self.removeItem(self.itemToDraw)
                    self.finish_drawing()

    def finish_drawing(self):
        self.itemToDraw = 0
        self.mouse_press = QPointF()

    def split_polyline(self, polyline_index, split_index):
        for item in self.items():
            if item.type == Item_Type.Polyline and item.index == polyline_index:
                points_1, points_2, radii_1, radii_2 = self.polyline_points_radii(
                    item,
                    split_index,
                    split_index
                )
                if item.is_closed:
                    polyline = Polyline(*(points_2 + points_1[1::]))
                    self.addItem(polyline)
                else:        
                    polyline_1 = Polyline(*points_1)
                    polyline_2 = Polyline(*points_2)
                    polyline_1.create_arcs(*radii_1)
                    polyline_2.create_arcs(*radii_2)

                    self.addItem(polyline_1)
                    self.addItem(polyline_2)

                    item.scene().removeItem(item)
                break


    def double_split_polyline(self, polyline_index, split_index_1, split_index_2):
        for item in self.items():
            if item.type == Item_Type.Polyline and item.index == polyline_index:
                self.removeItem(item)
                points_1, points_2, radii_1, radii_2 = self.polyline_points_radii(
                    item,
                    split_index_1,
                    split_index_2
                )
                if item.is_closed:
                    polyline = Polyline(*(points_2 + points_1[1::]))
                    self.addItem(polyline)
                else:        
                    polyline_1 = Polyline(*points_1)
                    polyline_2 = Polyline(*points_2)
                    polyline_1.create_arcs(*radii_1)
                    polyline_2.create_arcs(*radii_2)
                    
                    if item.previous_layer_arc:
                        self.create_layer_arcs_starting(polyline_1, item.previous_layer_arc.r)
                    if item.next_layer_arc:
                        self.create_layer_arcs_ending(polyline_2, item.next_layer_arc.r)
                    
                    self.addItem(polyline_1)
                    self.addItem(polyline_2)
                polyline_3 = Polyline(
                    item.lines[split_index_1].points[0],
                    item.lines[split_index_1].points[1]
                )
                self.addItem(polyline_3)
                break


    def polyline_points_radii(self, polyline, split_index_1, split_index_2):
        points_1 = []
        radii_1 = []
        points_2 = []
        radii_2 = []
        for i, line in enumerate(polyline.lines):
            if i == 0:
                points_1.append(line.points[0])

            if line.index < split_index_1:
                points_1.append(line.points[1])
            elif line.index >= split_index_2:
                points_2.append(line.points[0])

            if i == len(polyline.points) - 2:
                points_2.append(line.points[1])

        for i, arc in enumerate(polyline.arcs):
            arcs_1_num  = len(points_1) - 2
            if i < arcs_1_num :
                radii_1.append(arc.r)
            elif i == arcs_1_num : 
                continue
            elif split_index_1 != split_index_2 and i == arcs_1_num  + 1:
                continue
            else:
                radii_2.append(arc.r)
    
        return points_1, points_2, radii_1, radii_2


    def remove_items(self):
        for item in self.selectedItems():
            if isinstance(item, Polyline):
                lines_to_remove = []
                for index, line in enumerate(item.lines):
                    if line.isSelected():
                        lines_to_remove.append(line.index)
                        
                self.remove_lines_from_polyline(item, *lines_to_remove)
                self.removeItem(item) 
            else:
                self.removeItem(item) 


    def remove_help_items(self):
        if self.help_item:
            self.removeItem(self.help_item)
            self.help_item = 0
        if self.help_line:
            self.removeItem(self.help_line)
            self.help_line = 0


    def remove_polyline(self, index):
        for item in self.items():
            if isinstance(item, Polyline) and item.index == index:
                item.remove_arcs()
                self.removeItem(item)


    def remove_lines_from_polyline(self, polyline, *line_indexes):
        if len(line_indexes) < len(polyline.lines):
            polylines_points = []
            firsts_lines_indexes = []
            previous_index = 0
            for line_index in line_indexes:
                if previous_index != line_index:
                    polylines_points.append(
                        polyline.points[previous_index:line_index+1]
                    )
                    firsts_lines_indexes.append(previous_index)
                previous_index = line_index + 1

            polylines_points.append(
                polyline.points[previous_index:len(polyline.points)]
            )

            # RADII
            radii_list = []
            previous_index = 0
            for line_index in line_indexes:
                radii = []
                if line_index == previous_index + 1:
                    radii_list.append([])
                elif line_index > previous_index + 1:
                    for i in range(previous_index, line_index - 1):
                        radii.append(polyline.arcs[i].r)
                    radii_list.append(radii)
                previous_index = line_index + 1
            
            radii = []
            for i in range(previous_index, len(polyline.lines)-1):
                radii.append(polyline.arcs[i].r)
            radii_list.append(radii)

            polylines = []
            for i, polyline_points_radii in enumerate(polylines_points):
                polylines.append(Polyline(*polyline_points_radii))
            
            for i, pol in enumerate(polylines):
                if len(pol.points) >= 2:
                    radii = radii_list[i] 
                    if len(radii) > 0:
                        pol.create_arcs(*radii)
                    self.addItem(pol)

            if polyline.lines[-1].index in line_indexes and self.next_layer_anchor and polyline.lines[-1].is_last_in_scene(self.next_layer_anchor.boundingRect()):
                self.remove_layer_arcs_ending()
            if polyline.lines[0].index in line_indexes and self.previous_layer_anchor and polyline.lines[0].is_first_in_scene(self.previous_layer_anchor.boundingRect()):
                self.remove_layer_arcs_starting()


    # -------- makeItemControllable
    def makeItemsControllable(self, areControllable):
        for item in self.items():
            item.setFlag(QGraphicsItem.ItemIsSelectable, areControllable)


    def drawBackground(self, painter, rect):
        painter.setPen(QPen(Qt.black, 0.0, Qt.SolidLine))

        points_offsets = [500, 400, 300, 200, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1]
        self.points_offset = None
        offset = 40
        min_points_num = 10
        rect = self.views()[0].mapToScene(self.views()[0].rect()).boundingRect()

        bottom_left, bottom_right, top_left = rect.bottomLeft(), rect.bottomRight(), rect.topLeft()

        width, height = rect.width(), rect.height()

        # points offset points number on axes calculation
        if height < width:
            for p_offset in points_offsets:
                points_num_vert = int(height / p_offset)
                if points_num_vert >= min_points_num:
                    points_num_hor = int(width / p_offset)
                    self.points_offset = p_offset
                    break
        else:
            for p_offset in points_offsets:
                points_num_hor = int(width / p_offset)
                if points_num_hor >= min_points_num:
                    points_num_vert = int(height / p_offset)
                    self.points_offset = p_offset
                    break

        # vertical axis
        ver_dists = []
        if bottom_left.y() * top_left.y() < 0:
            painter.drawLine(bottom_left.x() * 2, 0, bottom_right.x() * 2, 0)

            points_top_num = int(-top_left.y() / height * points_num_vert) + 5
            points_bottom_num = points_num_vert - points_top_num + 5
            for i in range(1, points_top_num + 1):
                ver_dists.append(- i * self.points_offset)
            ver_dists.append(0)
            for i in range(1, points_bottom_num + 1):
                ver_dists.append(i * self.points_offset)
        else:
            starting_y = - int(-bottom_left.y() / self.points_offset) * self.points_offset
            for i in range(1, points_num_vert + 1):
                ver_dists.append(starting_y - i * self.points_offset)
            
        # horizontal axis
        hor_dists = []
        if bottom_left.x() * bottom_right.x() < 0:
            painter.drawLine(0, bottom_left.y() * 2, 0, top_left.y() * 2)

            points_left_num = int(math.fabs(bottom_left.x()) / width * points_num_hor) +5
            points_right_num = points_num_hor - points_left_num + 5
            for i in range(1, points_left_num + 1):
                hor_dists.append(- i * self.points_offset)
            hor_dists.append(0)
            for i in range(1, points_right_num + 1):
                hor_dists.append(i * self.points_offset)
        else:
            starting_x = - int(-bottom_left.x() / self.points_offset) * self.points_offset
            for i in range(1, points_num_hor + 1):
                hor_dists.append(starting_x + i * self.points_offset)
            
        if self.parent.grid_action.isChecked():
            points = []

            offset = preferences.grid_offset

            w_num = int(width / offset)
            h_num = int(height / offset)

            h_grid_dists = [i * offset for i in range(h_num)]
            neg_h_grid_dists = [- o for o in h_grid_dists]
            h_grid_dists.extend(neg_h_grid_dists)

            v_grid_dists = [i * offset for i in range(w_num)]
            neg_v_grid_dists = [- o for o in v_grid_dists]
            v_grid_dists.extend(neg_v_grid_dists)

            for hor_dist in h_grid_dists:
                for ver_dist in v_grid_dists:
                    points.append(QPointF(float(hor_dist), float(ver_dist)))
            painter.drawPoints(*points)

        self.parent.update_x_axis(bottom_left.x(), width, hor_dists)
        self.parent.update_y_axis(bottom_left.y(), height, ver_dists)
        
        for scene in self.parent.scenes:
            if scene != self:
                for item in scene.items():
                    if isinstance(item, Polyline):
                        for it in item.childItems():
                            it.draw(painter, True)