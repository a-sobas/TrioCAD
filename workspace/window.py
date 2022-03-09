from PyQt5 import Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class SetPointWindow(QWidget):
    got_x = pyqtSignal(str)
    got_y = pyqtSignal(str)


    def __init__(self, parent):
        QWidget.__init__(self)

        self.count = 0

        self.initUI()


    def initUI(self):
        self.form_groupBox_point = QGroupBox('Point coordinates')

        layout_point = QFormLayout()

        self.edit_x = QLineEdit()
        self.edit_y = QLineEdit()

        layout_point.addRow(QLabel("X: "), self.edit_x)
        layout_point.addRow(QLabel("Y: "), self.edit_y)
        
        self.set_button = QPushButton('&Set')
        self.cancel_button = QPushButton('&Cancel')

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.set_button)
        layout_buttons.addWidget(self.cancel_button)

        self.form_groupBox_point.setLayout(layout_point)

        self.cancel_button.clicked.connect(self.close)

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.form_groupBox_point)
        layout_main.addLayout(layout_buttons)

        self.setLayout(layout_main)


class ChangePointRadiusWindow(QWidget):
    got_x = pyqtSignal(str)
    got_y = pyqtSignal(str)

    def __init__(self, parent):
        QWidget.__init__(self)

        self.count = 0

        self.initUI()

    def initUI(self):
        self.form_groupBox_r = QGroupBox('Radius')
        self.form_groupBox_point = QGroupBox('Point coordinates')

        layout_radius = QFormLayout()
        layout_point = QFormLayout()

        self.edit_r = QLineEdit()
        self.edit_x = QLineEdit()
        self.edit_y = QLineEdit()

        layout_radius.addRow(QLabel("R: "), self.edit_r)
        layout_point.addRow(QLabel("X: "), self.edit_x)
        layout_point.addRow(QLabel("Y: "), self.edit_y)
        
        self.set_button = QPushButton('&Set')
        self.cancel_button = QPushButton('&Cancel')

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.set_button)
        layout_buttons.addWidget(self.cancel_button)

        self.form_groupBox_r.setLayout(layout_radius)
        self.form_groupBox_point.setLayout(layout_point)

        self.cancel_button.clicked.connect(self.close)


        layout_main = QVBoxLayout()
        layout_main.addWidget(self.form_groupBox_r)
        layout_main.addWidget(self.form_groupBox_point)
        layout_main.addLayout(layout_buttons)

        self.setLayout(layout_main)


class SetPointRadiusWindow(QWidget):
    got_x = pyqtSignal(str)
    got_y = pyqtSignal(str)


    def __init__(self, parent):
        QWidget.__init__(self)

        self.count = 0

        self.initUI()


    def initUI(self):
        self.form_groupBox_r = QGroupBox('Radius')
        self.form_groupBox_point = QGroupBox('Point coordinates')

        layout_radius = QFormLayout()
        layout_point = QFormLayout()

        self.edit_r = QLineEdit()
        self.edit_x = QLineEdit()
        self.edit_y = QLineEdit()

        layout_radius.addRow(QLabel("R: "), self.edit_r)
        layout_point.addRow(QLabel("X: "), self.edit_x)
        layout_point.addRow(QLabel("Y: "), self.edit_y)
        
        self.add_button = QPushButton('Add')
        self.cancel_button = QPushButton('Cancel')

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.add_button)
        layout_buttons.addWidget(self.cancel_button)

        self.form_groupBox_r.setLayout(layout_radius)
        self.form_groupBox_point.setLayout(layout_point)

        self.cancel_button.clicked.connect(self.close)


        layout_main = QVBoxLayout()
        layout_main.addWidget(self.form_groupBox_r)
        layout_main.addWidget(self.form_groupBox_point)
        layout_main.addLayout(layout_buttons)

        self.setLayout(layout_main)


class CreatePolylineWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)

        self.point_count = 0
        self.points_x_edit = []
        self.points_y_edit = []
        self.radii_edit = []

        self.create_polyline = None
        self.add_point_to_polyline = None
        self.update_polyline_points = None
        self.update_polyline_radii = None
        self.remove_window_polyline = None

        self.initUI()

        self.setFixedWidth(300)


    def initUI(self):

        self.starting_point_box = QGroupBox('Starting point')
        self.starting_point_layout = QHBoxLayout()
        self.starting_point_layout.addWidget(QLabel('X: '))
        self.points_x_edit.append(QLineEdit('0'))
        self.points_x_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.starting_point_layout.addWidget(self.points_x_edit[-1])
        self.starting_point_layout.addWidget(QLabel(' Y: '))
        self.points_y_edit.append(QLineEdit('0'))
        self.points_y_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.starting_point_layout.addWidget(self.points_y_edit[-1])
    
        self.starting_point_box.setLayout(self.starting_point_layout)

        self.sp_dr_layout = QHBoxLayout()

        self.default_radius_groubpox = QGroupBox('Default radius')
        self.default_radius_layout = QHBoxLayout()
        self.default_radius_edit = QLineEdit('0')
        self.default_radius_edit.setFixedWidth(50)
        self.default_radius_edit.editingFinished.connect(self.update_radii)
        self.default_radius_layout.addWidget(self.default_radius_edit)

        self.default_radius_groubpox.setLayout(self.default_radius_layout)

        self.sp_dr_layout.addWidget(self.starting_point_box)
        self.sp_dr_layout.addWidget(self.default_radius_groubpox)

        self.points_radii_layout = QGridLayout()
        self.points_radii_layout.setHorizontalSpacing(0)
        
        self.points_radii_layout.addWidget(QLabel('Point'), 0, 0)
        self.points_radii_layout.addWidget(QLabel('           X'), 0, 1)
        self.points_radii_layout.addWidget(QLabel('           Y'), 0, 2)
        self.points_radii_layout.addWidget(QLabel('         Radii'), 0, 3)

        self.points_radii_layout.addWidget(QLabel('  P1'), 1, 0)
        self.points_x_edit.append(QLineEdit('0'))
        self.points_x_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.points_radii_layout.addWidget(self.points_x_edit[-1], 1, 1)
        self.points_y_edit.append(QLineEdit('0'))
        self.points_y_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.points_radii_layout.addWidget(self.points_y_edit[-1], 1, 2)
        self.point_count += 1

        self.points_radii_layout.setAlignment(Qt.AlignCenter)

        self.add_remove_layout = QHBoxLayout()
        self.add_button = QPushButton('&Add point')
        self.add_button.clicked.connect(self.add_row)
        self.remove_button = QPushButton('&Remove last')
        self.remove_button.clicked.connect(self.remove_last_row)
        self.add_remove_layout.addWidget(self.add_button)
        self.add_remove_layout.addWidget(self.remove_button)

        self.buttons_points_radii_layout = QVBoxLayout()
        self.buttons_points_radii_layout.addLayout(self.points_radii_layout)
        self.buttons_points_radii_layout.addLayout(self.add_remove_layout)

        self.main_box = QGroupBox('Points / Radii')
        self.main_box.setLayout(self.buttons_points_radii_layout)
        
        self.main_buttons_layout = QHBoxLayout()
        self.create_button = QPushButton('Cr&eate')
        self.create_button.clicked.connect(self.create)
        self.cancel_button = QPushButton('&Cancel')
        self.cancel_button.clicked.connect(self.cancel_window)
        self.main_buttons_layout.addWidget(self.create_button)
        self.main_buttons_layout.addWidget(self.cancel_button)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.sp_dr_layout)
        self.main_layout.addWidget(self.main_box)
        self.main_layout.addLayout(self.main_buttons_layout)

        self.setLayout(self.main_layout)


    def add_row(self):
        text_1 = '        R' + str(self.point_count)
        self.points_radii_layout.addWidget(QLabel(text_1), self.point_count*2, 2)
        self.radii_edit.append(
            [RadiiChanged(
                self.perform_polyline_radii_update,
                self.change_radii_background
            ),
            QLineEdit(self.default_radius_edit.text())
            ]
        )

        self.radii_edit[-1][1].setFixedWidth(50)
        self.r_changed_index = len(self.radii_edit) - 1
        self.radii_edit[-1][1].editingFinished.connect(self.radii_edit[-1][0].radii_update)
        self.points_radii_layout.addWidget(self.radii_edit[-1][1], self.point_count*2, 3)

        text_2 = '  P' + str(self.point_count + 1)
        self.points_radii_layout.addWidget(QLabel(text_2), self.point_count*2 + 1, 0)

        self.points_x_edit.append(QLineEdit('0'))
        self.points_x_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.points_radii_layout.addWidget(self.points_x_edit[-1], self.point_count*2 + 1, 1)

        self.points_y_edit.append(QLineEdit('0'))
        self.points_y_edit[-1].editingFinished.connect(self.perform_polyline_points_update)
        self.points_radii_layout.addWidget(self.points_y_edit[-1], self.point_count*2 + 1, 2)

        self.point_count += 1

        self.perform_add_point_to_polyline()
    

    def remove_last_row(self):
        pass


    def update_radii(self):
        for radius_edit in self.radii_edit:
            if not radius_edit[0].is_changed:
                radius_edit[1].setText(self.default_radius_edit.text())

        self.perform_polyline_radii_update()


    def perform_polyline_points_update(self):
        points = self.get_points()
        radii = self.get_radii()

        if points is not None:
            self.update_polyline_points([points, radii])
        else:
            pass


    def perform_polyline_radii_update(self):
        self.perform_polyline_points_update()


    def perform_add_point_to_polyline(self):
        x = self.get_value(self.points_x_edit[-1])
        y = self.get_value(self.points_y_edit[-1])
        r = self.get_value(self.radii_edit[-1][1])
        
        if x is not None and y is not None and r is not None:
            point = QPointF(x, y)

            self.add_point_to_polyline(point, r)
        else: 
            pass


    def get_points(self):
        points = []
        x_coordinates = []
        y_coordinates = []

        for x,y in zip(self.points_x_edit, self.points_y_edit):
            val_x = self.get_value(x)
            val_y = self.get_value(y)

            if val_x is not None:
                x_coordinates.append(val_x)
            else:
                return None

            if val_y is not None:
                y_coordinates.append(val_y)
            else:
                return None

        for x_coordinate, y_coordinate in zip(x_coordinates, y_coordinates):
            points.append(QPointF(x_coordinate, -y_coordinate))

        return points


    def get_radii(self):
        radii = []

        for radius in self.radii_edit:
            val_r = self.get_value(radius[1])

            if val_r is not None:
                radii.append(val_r)
            else:
                return None

        return radii


    def get_value(self, item):
        value = self.str_to_float(item.text())

        if value is not None:
            return value
        else:
            return None


    def str_to_float(self, s):
        result = None
        try:
            result = float(s)
        except:
            pass

        return result


    def create(self):
        self.perform_polyline_points_update()
        self.close()


    def cancel_window(self):
        self.remove_window_polyline()

        self.close()


    def change_radii_background(self, index):
        self.radii_edit[index][1].setStyleSheet('background-color : rgba(255, 0, 0, 100);')


class RadiiChanged():
    count = 0


    def __init__(self, update, change_background):
        self.update = update
        self.change_background = change_background

        self.index = RadiiChanged.count
        RadiiChanged.count += 1

        self.is_changed = False


    def radii_update(self):
        self.set_changed()

        self.change_background(self.index)

        self.update()


    def set_changed(self):
        self.is_changed = True


class ChangeDefaultRadiusWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)

        self.initUI()


    def initUI(self):
        self.default_radius_edit = QLineEdit('0')
        self.set_button = QPushButton('&Set')
        self.cancel_button = QPushButton('&Cancel')
        self.cancel_button.clicked.connect(self.close)

        horizontal_layout_radius = QHBoxLayout()
        horiznotal_layout_buttons = QHBoxLayout()
        main_layout = QVBoxLayout()

        horizontal_layout_radius.addWidget(QLabel('Default radius: '))
        horizontal_layout_radius.addWidget(self.default_radius_edit)

        horiznotal_layout_buttons.addWidget(self.set_button)
        horiznotal_layout_buttons.addWidget(self.cancel_button)

        main_layout.addLayout(horizontal_layout_radius)
        main_layout.addLayout(horiznotal_layout_buttons)

        self.setLayout(main_layout)


    def get_value(self, item):
        value = self.str_to_float(item.text())

        if value is not None:
            return value
        else:
            return None


    def str_to_float(self, s):
        result = None
        try:
            result = float(s)
        except:
            pass

        return result


class NewLayerWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)

        self.initUI()


    def initUI(self):
        self.layer_name = QLineEdit()
        self.create_button = QPushButton('C&reate')
        self.cancel_button = QPushButton('&Cancel')
        self.cancel_button.clicked.connect(self.close)

        horizontal_layout_radius = QHBoxLayout()
        horiznotal_layout_buttons = QHBoxLayout()
        main_layout = QVBoxLayout()

        horizontal_layout_radius.addWidget(QLabel('Layer name: '))
        horizontal_layout_radius.addWidget(self.layer_name)

        horiznotal_layout_buttons.addWidget(self.create_button)
        horiznotal_layout_buttons.addWidget(self.cancel_button)

        main_layout.addLayout(horizontal_layout_radius)
        main_layout.addLayout(horiznotal_layout_buttons)

        self.setLayout(main_layout)