from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from config.enums import Item_Type


class Coursor():
    size = 20

    def __init__(self):

        self.pos = QPointF()

    def set_pos(self, pos):
        self.pos = pos

    def covered_items(self, items, line_index=None, polyline_index=None):
        items = self.colliding_items(items)

        if line_index is not None:
            lines = [
                item for item
                in items
                if item.type == Item_Type.Line and self.is_correct_line(
                    item,
                    line_index,
                    polyline_index
                )
            ]
        else:
            lines = [item for item in items if item.type == Item_Type.Line]

        return lines

    def colliding_items(self, items):
        s = Coursor.size
        points = [
            self.pos,

            self.pos - QPointF(0, s),
            self.pos + QPointF(0, s),
            self.pos - QPointF(s, 0),
            self.pos + QPointF(s, 0),

            self.pos - QPointF(s, s),
            self.pos + QPointF(s, s),
            self.pos - QPointF(-s, s),
            self.pos + QPointF(-s, s)
        ]

        covered_items = []
        for item in items:
            for point in points:
                if item.boundingRect().contains(point):
                    covered_items.append(item)
                    break
        return covered_items

    def is_correct_line(self, line, line_index, polyline_index):
        if line.parentItem().index != polyline_index:
            return True
        elif line.parentItem().index == polyline_index and line.index != line_index:
            return True
        else:
            return False
