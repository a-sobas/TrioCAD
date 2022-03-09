from PyQt5.QtCore import *

import re
import math


def interpret(file_path):
    with open(file_path, "r") as f:
        f = f.read()
    
    entities = re.split('ENTITIES\n', f)[1]
    objects = re.split('  0\n', entities)[1:]

    arcs = []
    lines = []
    for obj in objects:
        obj_codes = re.split('\n', obj) 
        if obj_codes[0] == 'LINE':
            lines.append(line_obj_convert(obj_codes))
        elif obj_codes[0] == 'ARC':
            arcs.append(arc_obj_convert(obj_codes))

    result = get_points_radii(calculate_points_radii(next_lines_groups(lines), arcs))

    return result

def arc_obj_convert(arc_obj):
    previous_code = None
    for code in arc_obj:
        if previous_code == ' 10':
            arc_center_x = dxf_value_to_number(code)
        elif previous_code == ' 20':
            arc_center_y = dxf_value_to_number(code)
        elif previous_code == ' 40':
            radius = dxf_value_to_number(code)
        elif previous_code == ' 50':
            start_angle = dxf_value_to_number(code)
        elif previous_code == ' 51':
            end_angle = dxf_value_to_number(code)
        previous_code = code

    return QPointF(arc_center_x, -arc_center_y), radius, start_angle, end_angle

def line_obj_convert(line_obj):
    previous_code = None
    for code in line_obj:
        if previous_code == ' 10':
            x_1 = dxf_value_to_number(code)
        elif previous_code == ' 20':
            y_1 = dxf_value_to_number(code)
        elif previous_code == ' 11':
            x_2 = dxf_value_to_number(code)
        elif previous_code == ' 21':
            y_2 = dxf_value_to_number(code)
        previous_code = code

    return QLineF(x_1, -y_1, x_2, -y_2)

def next_lines_groups(lines):
    groups = []
    group = []

    while lines:
        line_0 = lines[0]
        group.append(lines[0])
        is_next_line = True
        while is_next_line: 
            is_next_line = False
            for i, line in enumerate(lines):
                if line != line_0:
                    if line.p1() == group[-1].p2():
                        is_next_line = True
                        group.append(line)
                        lines.remove(line)
                        break
                    elif line.p2() == group[-1].p2():
                        is_next_line = True
                        group.append(QLineF(line.p2(), line.p1()))
                        lines.remove(line)
                        break
                    elif line.p1() == group[0].p1():
                        is_next_line = True
                        group.insert(0, QLineF(line.p2(), line.p1()))
                        lines.remove(line)
                        break
                    elif line.p2() == group[0].p1():
                        is_next_line = True
                        group.insert(0, line)
                        lines.remove(line)
                        break

        groups.append(group)
        lines.remove(lines[0])
        group = []

    return groups

# struktura danych ['obiekt - line / arc', 'arc' : r / 'line' : line]
def calculate_points_radii(lines_groups, arcs):
    points_radii = []
    data = []

    while lines_groups:
        line_group_0 = lines_groups[0]
        data.append(['GROUP', line_group_0])
        is_next_line = True
        while is_next_line:
            is_next_line = False
            for i, line_group in enumerate(lines_groups):
                if line_group != line_group_0:
                    for arc in arcs:
                        center, r, a_1, a_2 = arc[0], arc[1], math.radians(arc[2]), math.radians(arc[3])
                        
                        arc_points_dxf = (
                            center + QPointF(r * math.cos(a_1), -r * math.sin(a_1)),
                            center + QPointF(r * math.cos(a_2), -r * math.sin(a_2))
                            )
                        arc_points = [line_group[0].p1(), data[0][1][0].p1()]
                        if not is_next_line and compare_points(arc_points_dxf, arc_points):
                            is_next_line = True
                            data.insert(0, ['ARC', r])
                            data.insert(0, ['GROUP', reverse_group(line_group)])
                            lines_groups.remove(line_group)
                            arcs.remove(arc)
                            break
                        arc_points = [line_group[0].p1(), data[-1][1][-1].p2()]
                        if not is_next_line and  compare_points(arc_points_dxf, arc_points):
                            is_next_line = True
                            data.append(['ARC', r])
                            data.append(['GROUP', line_group])
                            lines_groups.remove(line_group)
                            arcs.remove(arc)
                            break
                        arc_points = [line_group[-1].p2(), data[0][1][0].p1()]
                        if not is_next_line and  compare_points(arc_points_dxf, arc_points):       
                            is_next_line = True
                            data.insert(0, ['ARC', r])
                            data.insert(0, ['GROUP', line_group])
                            lines_groups.remove(line_group)
                            arcs.remove(arc)
                            break
                        arc_points = [line_group[-1].p2(), data[-1][1][-1].p2()]
                        if not is_next_line and  compare_points(arc_points_dxf, arc_points):
                            is_next_line = True
                            data.append(['ARC', r])
                            data.append(['GROUP', reverse_group(line_group)])
                            lines_groups.remove(line_group)
                            arcs.remove(arc)
                            break
                        
        points_radii.append(data)
        lines_groups.remove(lines_groups[0])
        data = []

    return points_radii

def get_points_radii(lines_radii_groups):
    previous_item_type = None
    points = []
    radii = []
    
    points_groups = []
    radii_groups = []
    for lines_radii_group in lines_radii_groups:
        
        for i, item in enumerate(lines_radii_group):

            if previous_item_type == 'ARC':
                radii.pop()
                points.pop()
                p = QPointF()
                lines_radii_group[i-2][1][-1].intersect(item[1][0], p)
                points.append(p)
                radii.append(lines_radii_group[i-1][1])

            if item[0] == 'GROUP':
                if not (previous_item_type == 'ARC'):
                    points.append(item[1][0].p1())
                for line in item[1]:
                    points.append(line.p2())
                    radii.append(0)
 
            previous_item_type = item[0]
        ##
        radii.pop()
        points_groups.append(points)
        if radii:
            radii_groups.append(radii)
        else:
            radii_groups.append([])

        radii = []
        points = []

    return points_groups, radii_groups

def reverse_group(group):
    g = group
    reversed_group = []
    
    g.reverse()
    for line in group:
        reversed_group.append(QLineF(line.p2(), line.p1()))

    return reversed_group

def compare_points(points_1, points_2):
    tolerance = 0.1
    
    are_fits = True
    for p_1, p_2 in zip(points_1, points_2):
        if not (math.hypot((p_1 - p_2).x(), (p_1 - p_2).y()) < tolerance):
            are_fits = False

    if are_fits:
        return are_fits

    are_fits = True

    points_1 = [points_1[1], points_1[0]]
    for p_1, p_2 in zip(points_1, points_2):
        if not (math.hypot((p_1 - p_2).x(), (p_1 - p_2).y()) < tolerance):
            are_fits = False
    
    return are_fits

def dxf_value_to_number(value):
    return int(str_to_float(value) * 1000) / 1000

def str_to_float(str):
    result = None
    try:
        result = float(str)
    except:
        pass

    return result