from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

from objects.polylinee import Polyline


def paths_to_basic(*scenes):
    polylines = []
    for i, scene in enumerate(scenes):
        scene_polylines = []
        for item in scene.items():
            if isinstance(item, Polyline):
                scene_polylines.append(item)

        if len(scene_polylines) == 1:
            polylines.append(scene_polylines[0])
        elif i != (len(scenes) - 1) and not len(scene_polylines) == 0: 
            return None

    basic_code = []
    if polylines:
        
        for i, polyline in enumerate(polylines):
            basic_code.append([])
            basic_code[i].append('\'' + scenes[i].name)
            if i == 0:
                basic_code[i].append(create_moveabs_command(polylines[0].lines[0].line.p1()))

            for j, line in enumerate(polyline.lines):
                real_line = line.create_real_line()

                if j > 0 and j < (len(polyline.lines)) and polyline.arcs[j-1].r != 0:
                    basic_code[i].append(create_movecirc_command(
                        polyline.arcs[j-1].points[1] - polyline.arcs[j-1].points[0], 
                        polyline.arcs[j-1].arc_center - polyline.arcs[j-1].points[0], 
                        2)
                    )

                if j == 0 and scenes[i].previous_layer_arc and scenes[i].previous_layer_arc.r != 0:
                    if j == 0 and scenes[i].next_layer_arc and scenes[i].next_layer_arc.r != 0:
                        offset = scenes[i].next_layer_arc.points[0] - scenes[i].previous_layer_arc.points[1]
                    else:
                        offset = real_line.p2() - scenes[i].previous_layer_arc.points[1]
                    dx = str(int(offset.x() * 1000) / 1000)
                    dy = str(-int(offset.y() * 1000) / 1000)
                    basic_code[i].append('    MOVE(' + dx + ', ' + dy + ')')
                    if len(polyline.lines) == 1 and scenes[i].next_layer_arc and scenes[i].next_layer_arc.r != 0:
                        basic_code[i].append('')
                        basic_code[i].append(create_movecirc_command(
                            scenes[i].next_layer_arc.points[1] - scenes[i].next_layer_arc.points[0],
                            scenes[i].next_layer_arc.arc_center - scenes[i].next_layer_arc.points[0], 
                            2)
                        )
                elif j < (len(polyline.lines)-1): 
                    basic_code[i].append(create_move_command(real_line))
                elif scenes[i].next_layer_arc and scenes[i].next_layer_arc.r != 0:
                    offset = scenes[i].next_layer_arc.points[0] - real_line.p1()
                    dx = str(int(offset.x() * 1000) / 1000)
                    dy = str(-int(offset.y() * 1000) / 1000)
                    basic_code[i].append('    MOVE(' + dx + ', ' + dy + ')')
                    basic_code[i].append('')
                    basic_code[i].append(create_movecirc_command(
                        scenes[i].next_layer_arc.points[1] - scenes[i].next_layer_arc.points[0],
                        scenes[i].next_layer_arc.arc_center - scenes[i].next_layer_arc.points[0], 
                        2)
                    )
                else:
                    basic_code[i].append(create_move_command(real_line))

                previous_real_line = real_line

    return basic_code

def create_moveabs_command(point):
    x = str(int(point.x() * 1000) / 1000)
    y = str(-int(point.y() * 1000) / 1000)

    return '    MOVEABS(' + x + ', ' + y + ')'

def create_move_command(real_line):
    dx = str(int(real_line.dx() * 1000) / 1000)
    dy = str(-int(real_line.dy() * 1000) / 1000)

    return '    MOVE(' + dx + ', ' + dy + ')'

def create_movecirc_command(vector_to_end_point, vector_to_center_point, dir):
    x_1 = str(int(vector_to_end_point.x() * 1000) / 1000)
    y_1 = str(int(- vector_to_end_point.y() * 1000) / 1000)

    x_2 = str(int(vector_to_center_point.x() * 1000) / 1000)
    y_2 = str(int(- vector_to_center_point.y() * 1000) / 1000)

    return '    MOVECIRC(' + x_1 + ', ' + y_1 + ', ' + x_2 + ', ' + y_2 + ', ' + str(dir) + ')'