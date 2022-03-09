from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import *


def line_param(p1, p2):
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()

    a = (y2 - y1) / (x2 - x1)
    b = (y1 - y2) / (x1 - x2) * x1 + y1

    return a, b


def translate_lines(r, line_1, line_2):
    normal_1 = line_1.normalVector()
    normal_2 = line_2.normalVector()

    angle = line_1.angleTo(line_2)
    if angle > 180 and angle < 360:
        normal_1.setAngle(normal_1.angle() + 180)
        normal_2.setAngle(normal_2.angle() + 180)

    normal_1.setLength(r)
    normal_2.setLength(r)

    l_1 = line_1.translated(normal_1.p2() - normal_1.p1())
    l_2 = line_2.translated(normal_2.p2() - normal_2.p1())

    return (normal_1, normal_2), (l_1, l_2)

def calculate_characteristic_arc_parameters(r, line_1, line_2):
    normal_lines, lines = translate_lines(r, line_1, line_2)

    points = calculate_characteristic_points(
        normal_lines,
        lines,
        line_1,
        line_2
    )

    return points


def calculate_characteristic_points(normal_lines, lines, line_1, line_2):
    arc_center = QPointF()
    char_point_1 = QPointF()
    char_point_2 = QPointF()

    lines[0].intersect(lines[1], arc_center)

    normal_lines[0].translate(arc_center - normal_lines[0].p2())
    normal_lines[1].translate(arc_center - normal_lines[1].p2())

    normal_lines[0].intersect(line_1, char_point_1)
    normal_lines[1].intersect(line_2, char_point_2)

    return arc_center, char_point_1, char_point_2


def calculate_characteristic_angles(line_1, line_2):
    angle = line_1.angleTo(line_2)
    if angle > 180 and angle < 360:
        start_angle = line_2.angle() - 180
        span_angle = line_1.angle() - 180 - start_angle
    else:
        start_angle = line_1.angle() - 180
        span_angle = line_2.angle() - 180 - start_angle

    return start_angle, span_angle