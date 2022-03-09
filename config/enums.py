from enum import Enum


class Line_Pos(Enum):
    First = 0,
    Between = 1,
    Last = 2,
    Lonely = 3


class Item_Type(Enum):
    Line = 0,
    Polyline = 1, 
    Rect = 2,
    Circle = 3,
    Arc = 4


class Item_Mode(Enum):
    Creating = 0,
    Showing = 1
