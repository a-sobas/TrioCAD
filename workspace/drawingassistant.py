from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math as m

from utils.RectF import RectF
from config.enums import Line_Pos
from config.enums import Item_Type
import config.preferences as preferences


class DrawingAssistant():

    max_dist_to_help_point = preferences.size_factor * 2.5
    max_dist_to_set_point = preferences.size_factor

    def __init__(self):
        self.count = 0
        self.mouse_press = QPointF()

        self.earlier_near_points = []

        self.n_point = None
        self.n_point_item = None
        self.n_point_item_brush = Qt.yellow
        self.help_line = 0

        self.draw_item_flag = False
        self.set_p_flag = False

        self.polyline_to_add = None
        self.points_to_add = []
        self.radii_to_add = []

    def calculate_pos(
        self, 
        actual_pos, 
        items, 
        item_to_draw_index, 
        grid_size,
        attraction_to_point_action, 
        orto_action, 
        attraction_to_grid_action
        ):

        DrawingAssistant.max_dist_to_help_point = preferences.size_factor * 2.5
        DrawingAssistant.max_dist_to_set_point = preferences.size_factor

        if self.set_p_flag:
            self.mouse_press = self.n_point

        if attraction_to_point_action:
            self.nearest_point(actual_pos, items, item_to_draw_index)

        self.help_line = 0

        if orto_action and not self.set_p_flag:
            self.look_for_help_line(actual_pos)

        if attraction_to_grid_action and not self.set_p_flag and not self.help_line:
            self.attraction(actual_pos, grid_size)

        if self.n_point:
            return self.n_point
        else:
            return actual_pos

    def attraction(self, actual_pos, grid_size):
        pos_x = int(actual_pos.x() / grid_size) * grid_size
        pos_y = int(actual_pos.y() / grid_size) * grid_size
        self.n_point = QPointF(pos_x, pos_y)

    def nearest_point(self, actual_pos, items, item_to_draw_index):
        if not items:
            self.reset_near_point_items()
        else:
            for item in items:
                for i, point in enumerate(item.points):
                    self.choose_nearest_point(actual_pos, point)
                    if self.set_p_flag:
                        self.addition(item, item_to_draw_index, i)
                        break

    def addition(self, line, item_to_draw_index, i):
        if line.type == Item_Type.Line and not line.parentItem().is_closed:
            points = line.parentItem().points
            arcs_to_add = []
            if (line.line_pos == Line_Pos.First or line.line_pos == Line_Pos.Lonely) and i == 0:
                self.polyline_to_add = line.parentItem()
                if item_to_draw_index:
                    self.points_to_add = points[0::]
                    arcs_to_add = line.parentItem().arcs[0::]
                    radii = []
                    radii.append(preferences.default_radius)
                    for arc in arcs_to_add:
                        radii.append(arc.r)
                    self.radii_to_add = radii
                else:
                    self.points_to_add = points[::-1]
                    arcs_to_add = line.parentItem().arcs[::-1]
                    radii = []
                    for arc in arcs_to_add:
                        radii.append(arc.r)
                    radii.append(preferences.default_radius)
                    self.radii_to_add = radii

            elif (line.line_pos == Line_Pos.Last or line.line_pos == Line_Pos.Lonely) and i == 1:
                self.polyline_to_add = line.parentItem()
                if item_to_draw_index:
                    self.points_to_add = points[::-1]
                    arcs_to_add = line.parentItem().arcs[::-1]
                    radii = []
                    radii.append(preferences.default_radius)
                    for arc in arcs_to_add:
                        radii.append(arc.r)
                    self.radii_to_add = radii
                else:
                    self.points_to_add = points[0::]
                    arcs_to_add = line.parentItem().arcs[0::]
                    radii = []
                    for arc in arcs_to_add:
                        radii.append(arc.r)
                    radii.append(preferences.default_radius)
                    self.radii_to_add = radii
                        
            else:
                self.points_to_add = []
                self.radii_to_add = []
                self.polyline_to_add = None

    def choose_nearest_point(self, actual_pos, point):
        dist = self.dist_between_points(point, actual_pos)
        if dist <= DrawingAssistant.max_dist_to_help_point:
            self.create_near_point_item(point)
            if dist <= DrawingAssistant.max_dist_to_set_point:
                self.set_point_flags(True, True)
                self.n_point = point
            else:
                self.set_point_flags(True)
                self.n_point = None
        else:
            self.reset_near_point_items()

    def create_near_point_item(self, point):
        self.n_point_item = QGraphicsRectItem(
            RectF.rect_from_center(
                point,
                preferences.size_factor/1.5,
                preferences.size_factor/1.5
            )
        )
        self.n_point_item.setPen(QPen(Qt.yellow, 0.0, Qt.SolidLine))
        self.n_point_item.setBrush(Qt.yellow)

    def reset_near_point_items(self):
        self.n_point = None
        self.n_point_item = None

        self.polyline_to_add = None
        self.points_to_add = []

        self.set_point_flags()

    def set_point_flags(self, draw_flag=False, set_flag=False):
        self.draw_item_flag = draw_flag
        if set_flag:
            self.set_p_flag = True
            self.n_point_item_brush = Qt.red
        else:
            self.set_p_flag = False
            self.n_point_item_brush = Qt.yellow

    def is_courser_over_object(self, coursor_pos, obj):
        if obj.boundingRect().contains(coursor_pos):
            return True
        else:
            return False

    def dist_between_points(self, p1, p2):
        return m.sqrt(m.pow(p1.x() - p2.x(), 2) + m.pow(p1.y() - p2.y(), 2))

    def look_for_help_line(self, actual_pos):

        xp, yp = self.mouse_press.x(), self.mouse_press.y()
        xm, ym = actual_pos.x(), actual_pos.y()

        line = QLineF(self.mouse_press, actual_pos)
        angle = line.angle()
        if angle > 355 or angle < 5:
            self.n_point = QPointF(xm, yp)
            self.help_line = QGraphicsLineItem(
                self.mouse_press.x(),
                self.mouse_press.y(),
                xm + 1000,
                yp
            )
        elif angle > 175 and angle < 185:
            self.n_point = QPointF(xm, yp)
            self.help_line = QGraphicsLineItem(
                self.mouse_press.x(),
                self.mouse_press.y(),
                xm - 1000,
                yp
            )
        elif angle > 85 and angle < 95:
            self.n_point = QPointF(xp, ym)
            self.help_line = QGraphicsLineItem(
                self.mouse_press.x(),
                self.mouse_press.y(),
                xp,
                ym - 1000
            )
        elif angle > 265 and angle < 275:
            self.n_point = QPointF(xp, ym)
            self.help_line = QGraphicsLineItem(
                self.mouse_press.x(),
                self.mouse_press.y(),
                xp,
                ym + 1000
            )
        else:
            self.help_line = 0

        if self.help_line:
            self.help_line.setPen(QPen(Qt.black, 0, Qt.DashDotDotLine))
