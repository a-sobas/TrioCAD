import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *

from workspace.scene import Scene
from workspace.scene import Mode
from objects.line import Line
from objects.arc import Arc
from objects.polylinee import Polyline
from objects.layeranchor import LayerAnchor
from workspace.xaxis import XAxis
from workspace.yaxis import YAxis
import interpreter.dxfinterpreter as dxfinterpreter
import to_trio_basic.conversion as conversion
import config.preferences as preferences
from workspace.window import CreatePolylineWindow
from workspace.window import ChangeDefaultRadiusWindow
from workspace.window import NewLayerWindow
from objects.handles.handle import Handle
from config.enums import Item_Mode


class View(QGraphicsView):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self._zoom = 20
        
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)

        self.setViewport(QGLWidget())
        self.setRenderHints(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)


    def mouseMoveEvent(self, e):
        pos = e.pos()
        pos = self.mapToScene(pos)
        self.parent().parentWidget().show_message(
            str(int(1000 * pos.x()) / 1000), 
            str(-int(1000 * pos.y()) / 1000)
            )

        super().mouseMoveEvent(e)


    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            f = 1.2
            self._zoom += 1
        else:
            factor = 0.8
            f = 0.83
            self._zoom -= 1

        if self._zoom > 0:
            self.scale(factor, factor)
            Handle.size /= f
            preferences.size_factor /= f
        elif self._zoom == 20:
            self.setTransform(QTransform())
            Handle.size = 10
        else:
            self._zoom = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.scenes = []
        self.edit = QTextEdit()
        self.edit.setMinimumWidth(350)
        self.new_layer_window = None
        self.createScenes()
        
        self.initUI()
        self.layer_combobox.addItem('Layer 0')
        self.actual_scene.name = self.layer_combobox.currentText()

        self.grid_action.triggered.connect(self.actual_scene.update)

        self.show()
        

    def createScenes(self):
        self.create_scene()
        self.view = View(self.actual_scene)
        self.view.setParent(self)

        self.axis_size = 20

        self.axis_x_scene = XAxis(self)
        self.axis_y_scene = YAxis(self)
        self.axes_scene = QGraphicsScene(self)
        self.axis_x_scene.setSceneRect(
            -self.actual_scene.width() / 2, 
            0, 
            self.actual_scene.width(), 
            self.axis_size
        )

        self.axis_y_scene.setSceneRect(
            -self.axis_size, 
            -self.actual_scene.height() / 2, 
            self.axis_size, 
            self.actual_scene.height()
        )

        self.axes_scene.setSceneRect(
            -self.axis_size, 
            -self.axis_size, 
            self.axis_size, 
            self.axis_size
        )

        self.axis_x_scene.addItem(
            QGraphicsLineItem(
                -self.axis_x_scene.width() / 2, 
                0, 
                self.axis_x_scene.width() / 2, 
                0
            )
        )

        self.axis_y_scene.addItem(
            QGraphicsLineItem(
                -1, 
                -self.axis_y_scene.height() / 2, 
                -1, 
                self.axis_y_scene.height() / 2 
            )
        )

        self.axis_x_view = QGraphicsView(self.axis_x_scene)
        self.axis_y_view = QGraphicsView(self.axis_y_scene)
        self.axes_view = QGraphicsView(self.axes_scene)
        
        self.axis_x_view.setFixedHeight(self.axis_size)
        self.axis_y_view.setFixedWidth(self.axis_size)
        self.axes_view.setFixedHeight(self.axis_size)
        self.axes_view.setFixedWidth(self.axis_size)

        self.axis_x_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.axis_y_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.axes_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.axis_x_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.axis_y_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.axes_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.axis_x_view.setFrameShape(QFrame.NoFrame)
        self.axis_y_view.setFrameShape(QFrame.NoFrame)
        self.axes_view.setFrameShape(QFrame.NoFrame)
        
        self.horizontalGroupBox = QGroupBox()
        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        
        layout.addWidget(self.axis_y_view, 0, 0)
        layout.addWidget(self.view, 0, 1)
        layout.addWidget(self.axes_view, 1, 0)
        layout.addWidget(self.axis_x_view, 1, 1)  

        layout.setSpacing(0)      

        self.horizontalGroupBox.setLayout(layout)
        self.setCentralWidget(self.horizontalGroupBox)


    def convert(self):
        self.edit.clear()
        code = conversion.paths_to_basic(*self.scenes)

        if code:
            for i, p in enumerate(code):
                if i != 0:
                    self.edit.append('')
                for j, c in enumerate(p):
                    if j == 0:
                        self.edit.setTextColor(Qt.blue)
                        self.edit.setFontItalic(True)
                        self.edit.append(c)
                        self.edit.setTextColor(Qt.black)
                        self.edit.setFontItalic(False)
                    else:
                        self.edit.append(c)


    def update_x_axis(self, zero_pos, width, hor_dists):
        rect = self.axis_x_view.mapToScene(self.axis_x_view.rect()).boundingRect()

        bottom_left = rect.bottomLeft()
        axis_width = rect.width()

        scale = axis_width / width

        axis_x_zero_pos = bottom_left.x() - zero_pos * scale

        dists = []
        for dist in hor_dists:
            dists.append(axis_x_zero_pos + dist * scale)

        self.axis_x_scene.x_dists = dists
        self.axis_x_scene.x_texts = hor_dists 
        self.axis_x_scene.update()


    def update_y_axis(self, zero_pos, height, ver_dists):
        rect = self.axis_y_view.mapToScene(self.axis_y_view.rect()).boundingRect()

        bottom_left = rect.bottomLeft()
        axis_height = rect.height()

        scale = axis_height / height

        axis_y_zero_pos = bottom_left.y() - zero_pos * scale

        dists = []
        for dist in ver_dists:
            dists.append(axis_y_zero_pos + dist * scale)

        self.axis_y_scene.y_dists = dists
        self.axis_y_scene.y_texts = ver_dists 
        self.axis_y_scene.update()

        
# -------- initUI
    def initUI(self):
        self.createActions()
        self.createConnections()

        self.create_menu_bar()
        self.createToolBar()
        self.create_status_bar()

        self.setDockOptions(QMainWindow.AnimatedDocks)
        self.edit_dock_widget = QDockWidget()
        self.edit_dock_widget.setWidget(self.edit)
        self.addDockWidget(Qt.RightDockWidgetArea, self.edit_dock_widget)


    def create_status_bar(self):
        self.statusBar().showMessage('')
        self.statusBar().setStyleSheet('color : red')


    def show_message(self, str_x, str_y):
        self.x_pos_status_bar.setText(str_x)
        self.y_pos_status_bar.setText(str_y)


    def show_info(self, info):
        self.statusBar().showMessage(info)


# -------- actionGroupClicked
    def actionGroupClicked(self, action):
        self.actual_scene.setMode(Mode(action.data()))


# -------- createAction
    def createActions(self):
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.create_new_project_window)
        self.new_action.setIcon(QIcon('icons2\icons8-create-30.png'))

        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self.save_project)
        self.save_action.setIcon(QIcon('icons2\icons8-save-30.png'))

        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_project)
        self.open_action.setIcon(QIcon('icons2\icons8-edit-file-30.png'))

        self.import_action = QAction('Import', self)
        self.import_action.triggered.connect(self.import_dxf)
        self.import_action.setIcon(QIcon('icons2\icons8-import-30.png'))

        self.lineAction = QAction('Polyline', self)
        self.lineAction.setData(Mode.DrawLine)
        self.lineAction.setIcon(QIcon('icons2\icons8-polyline-30.png'))
        self.lineAction.setCheckable(True)

        self.polyline_from_table_action = QAction('Polyline from table', self)
        self.polyline_from_table_action.triggered.connect(self.polyline_window)
        self.polyline_from_table_action.setIcon(QIcon('icons2\icons8-bulleted-list-30.png'))

        self.default_radius_action = QAction('R', self)
        self.default_radius_action.triggered.connect(self.create_default_radius_window)
        self.default_radius_action.setIcon(QIcon('icons2\icons8-radius-30.png'))

        self.selectAction = QAction("Modify", self)
        self.selectAction.setData(Mode.SelectObject)
        self.selectAction.setIcon(QIcon('icons2\icons8-design-30.png'))
        self.selectAction.setCheckable(True)

        self.add_layer_action = QAction('Add layer', self)
        self.add_layer_action.triggered.connect(self.create_new_layer_window)
        self.add_layer_action.setIcon(QIcon('icons2\icons8-unchecked-checkbox-30.png'))

        self.delete_layer_action = QAction('Delete layer', self)
        self.delete_layer_action.triggered.connect(self.delete_layer)
        self.delete_layer_action.setIcon(QIcon('icons2\icons8-unchecked-checkbox-30 (1).png'))

        self.previous_layer_action = QAction('Previous layer', self)
        self.previous_layer_action.triggered.connect(self.change_to_previous)
        self.previous_layer_action.setIcon(QIcon('icons2\icons8-back-to-30.png'))

        self.next_layer_action = QAction('Next layer', self)
        self.next_layer_action.triggered.connect(self.change_to_next)
        self.next_layer_action.setIcon(QIcon('icons2\icons8-next-page-30.png'))

        self.change_mode_action = QAction('Mode', self)
        self.change_mode_action.triggered.connect(self.change_mode)
        self.change_mode_action.setIcon(QIcon('icons2\icons8-available-updates-30.png'))

        self.convert_action = QAction('Convert', self)
        self.convert_action.triggered.connect(self.convert)
        self.convert_action.setIcon(QIcon('icons2\icons8-play-graph-report-30.png'))

        self.attraction_to_point_action = QAction("Attraction to point", self)
        self.attraction_to_point_action.setIcon(QIcon('icons2\icons8-collect-30.png'))
        self.attraction_to_point_action.setCheckable(True)
        self.attraction_to_point_action.setChecked(True)

        self.orto_action = QAction("Orto", self)
        self.orto_action.setIcon(QIcon('icons2\icons8-perpendicular-symbol-30.png'))
        self.orto_action.setCheckable(True)
        self.orto_action.setChecked(True)

        self.attraction_action = QAction("Attraction", self)
        self.attraction_action.setIcon(QIcon('icons2\icons8-circled-menu-30.png'))
        self.attraction_action.setCheckable(True)

        self.grid_action = QAction("Grid", self)
        self.grid_action.setIcon(QIcon('icons2\icons8-grid-30.png'))
        self.grid_action.setCheckable(True)

        self.actionGroup = QActionGroup(self)
        self.actionGroup.setExclusive(True)

        self.actionGroup.addAction(self.lineAction)
        self.actionGroup.addAction(self.selectAction)


    def create_new_project_window(self):
        msgBox = QMessageBox()
        msgBox.setText("New project creation.")
        msgBox.setInformativeText("Do you want to create new project?")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        
        ret = msgBox.exec()

        if ret == QMessageBox.Ok:
            self.create_new_project()
        elif ret == QMessageBox.Cancel:
            pass


    def create_new_project(self):
        self.view.setScene(None)
        self.layer_combobox.clear()
        self.actual_scene = None
        self.scenes = []

        self.create_scene()
        self.view.setScene(self.actual_scene)
        self.layer_combobox.addItem('Layer 0')
    

    def create_default_radius_window(self):
        self.default_radius_window = ChangeDefaultRadiusWindow(self)
        self.default_radius_window.set_button.clicked.connect(self.set_default_radius)

        self.default_radius_window.move(self.mapToGlobal(QPoint(self.width()/2, self.height()/2)))
        self.default_radius_window.show()


    def set_default_radius(self):
        preferences.default_radius = self.str_to_float(
            self.default_radius_window.default_radius_edit.text()
        )
        self.default_radius_status_bar.setText(str(preferences.default_radius))
        self.default_radius_window.close()


    def str_to_float(self, s):
        result = None
        try:
            result = float(s)
        except:
            pass

        return result


    def change_to_previous(self):
        index = self.scenes.index(self.actual_scene)

        if index > 0:
            arc = self.actual_scene.previous_layer_arc
            polyline = None
            if self.actual_scene.first_polyline():
                polyline = self.actual_scene.first_polyline()
            self.layer_combobox.setCurrentIndex(index - 1)
            self.actual_scene = self.scenes[index - 1]
            
            if arc is not None and self.actual_scene.next_scene() and self.actual_scene.next_scene().first_polyline():
                self.actual_scene.create_layer_arcs_ending(
                    self.actual_scene.last_polyline(), 
                    arc.r
                    )
            elif polyline and arc is not None:
                self.actual_scene.create_layer_arcs_ending(
                    polyline, 
                    arc.r
                    )
            else:
                self.actual_scene.remove_layer_arcs_ending()
            
            self.view.setScene(self.actual_scene)

        self.grid_action.triggered.connect(self.actual_scene.update)


    def change_to_next(self):
        index = self.scenes.index(self.actual_scene)

        if index < (len(self.scenes) - 1):
            arc = self.actual_scene.next_layer_arc
            polyline = None
            if self.actual_scene.last_polyline():
                polyline = self.actual_scene.last_polyline()
            self.layer_combobox.setCurrentIndex(index + 1)
            self.actual_scene = self.scenes[index + 1]
            
            if arc is not None and self.actual_scene.previous_scene() and self.actual_scene.previous_scene().last_polyline():
                self.actual_scene.create_layer_arcs_starting(
                    self.actual_scene.first_polyline(), 
                    arc.r
                    )
            elif polyline and arc is not None:
                self.actual_scene.create_layer_arcs_starting(
                    polyline, 
                    arc.r
                    )
            else:
                self.actual_scene.remove_layer_arcs_starting()
            
            self.view.setScene(self.actual_scene)

        self.grid_action.triggered.connect(self.actual_scene.update)


    def import_dxf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            'QFileDialog.getOpenFileName()', 
            '', 
            'DXF files (*.dxf)', 
            options = options
        )
        if file_name:
            points_groups, radii_groups = dxfinterpreter.interpret(file_name)

            for points_group, radii_group in zip(points_groups, radii_groups): 
                item = Polyline(*points_group)
                if radii_group:
                    item.create_arcs(*radii_group)
                self.actual_scene.addItem(item)
        

    def create_scene(self):
        if len(self.scenes) == 0:
            self.scenes.append(Scene(self, 0))
        else:
            self.scenes.append(Scene(self, self.actual_scene.index + 1))
        self.actual_scene = self.scenes[-1]
        if self.new_layer_window:
            self.actual_scene.name = self.new_layer_window.layer_name.text()
        self.new_layer_window = None
        self.actual_scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setMouseTracking(True)


    def create_new_layer_window(self):
        self.new_layer_window = NewLayerWindow(self)
        self.new_layer_window.create_button.clicked.connect(self.add_layer)

        self.new_layer_window.move(self.mapToGlobal(QPoint(self.width()/2, self.height()/2)))
        self.new_layer_window.show()


    def add_layer(self):
        polylines_num = 0
        last_point = None
        polyline = None
        for item in self.actual_scene.items():
            if isinstance(item, Polyline):
                polylines_num = polylines_num + 1
                last_point = item.points[-1]
                polyline = item
                
        if polylines_num == 1:
            self.actual_scene.next_layer_anchor = LayerAnchor(last_point)
            self.actual_scene.addItem(self.actual_scene.next_layer_anchor)
            
            self.create_scene()
            self.actual_scene.previous_layer_anchor = LayerAnchor(last_point)
            self.actual_scene.addItem(self.actual_scene.previous_layer_anchor)

            self.view.setScene(self.actual_scene)
            self.layer_combobox.addItem(self.actual_scene.name)
            self.layer_combobox.setCurrentText(self.actual_scene.name)
            self.actual_scene.name = self.layer_combobox.currentText()


    def delete_layer(self):
        if len(self.scenes) > 1:
            if self.layer_combobox.currentIndex == (len(self.scenes) - 1):
                self.layer_combobox.setCurrentText(str(len(self.scenes)-2))
            self.layer_combobox.removeItem(-1)
            self.actual_scene.removeItem(self.actual_scene.previous_layer_anchor)
            self.actual_scene.previous_layer_anchor = None
            self.scenes.pop()
            self.actual_scene = self.scenes[-1]
            self.actual_scene.removeItem(self.actual_scene.next_layer_anchor)
            self.actual_scene.next_layer_anchor = None
            self.view.setScene(self.actual_scene)

            self.grid_action.triggered.connect(self.actual_scene.update)
        

    def change_scene(self):
        self.actual_scene = self.scenes[self.layer_combobox.currentIndex()]
        self.view.setScene(self.actual_scene)
        self.actual_scene.update()

        self.grid_action.triggered.connect(self.actual_scene.update)


# -------- createConnection
    def createConnections(self):
        self.actionGroup.triggered.connect(self.actionGroupClicked)


# -------- createToolar
    def createToolBar(self):
        self.file_tool_bar = QToolBar()
        self.file_tool_bar.addActions((self.new_action, self.import_action))

        self.drawing_tool_bar = QToolBar()
        self.drawing_tool_bar.addAction(self.selectAction)
        self.drawing_tool_bar.addSeparator()

        self.drawing_tool_bar.addAction(self.lineAction)
        self.drawing_tool_bar.addAction(self.polyline_from_table_action)
        self.drawing_tool_bar.addAction(self.default_radius_action)

        self.layer_tool_bar = QToolBar()
        self.layer_tool_bar.addActions(
            (self.add_layer_action, self.delete_layer_action)
        )
        self.layer_tool_bar.addAction(self.previous_layer_action)
        self.layer_combobox = QComboBox(self)
        self.layer_combobox.currentIndexChanged.connect(self.change_scene)
        self.layer_tool_bar.addWidget(self.layer_combobox)
        self.layer_tool_bar.addAction(self.next_layer_action)

        self.mode_tool_bar = QToolBar()
        self.mode_tool_bar.addAction(self.change_mode_action)

        self.conversion_tool_bar = QToolBar()
        self.conversion_tool_bar.addAction(self.convert_action)

        self.status_assist_tool_bar = QToolBar()

        self.x_pos_status_bar = QLineEdit('0')
        self.x_pos_status_bar.setFixedWidth(70)
        self.x_pos_status_bar.setStyleSheet('background-color : rgb(240, 240, 240);')
        self.x_pos_status_bar.setReadOnly(True)

        self.y_pos_status_bar = QLineEdit('0')
        self.y_pos_status_bar.setFixedWidth(70)
        self.y_pos_status_bar.setStyleSheet('background-color : rgb(240, 240, 240);')
        self.y_pos_status_bar.setReadOnly(True)

        self.default_radius_status_bar = QLineEdit(str(preferences.default_radius))
        self.default_radius_status_bar.setFixedWidth(70)
        self.default_radius_status_bar.setStyleSheet('background-color : rgb(240, 240, 240);')
        self.default_radius_status_bar.setReadOnly(True)

        self.status_assist_tool_bar.addWidget(QLabel(' X: '))
        self.status_assist_tool_bar.addWidget(self.x_pos_status_bar)
        self.status_assist_tool_bar.addWidget(QLabel(' Y: '))
        self.status_assist_tool_bar.addWidget(self.y_pos_status_bar)
        self.status_assist_tool_bar.addWidget(QLabel(' R: '))
        self.status_assist_tool_bar.addWidget(self.default_radius_status_bar)
        
        self.status_assist_tool_bar.addSeparator()

        self.status_assist_tool_bar.addActions(
            (
                self.attraction_to_point_action,
                self.orto_action,
                self.attraction_action
            )
        )

        self.status_assist_tool_bar.addSeparator()

        self.status_assist_tool_bar.addAction(self.grid_action)

        self.grid_offset_edit = QLineEdit(str(preferences.grid_offset))
        self.grid_offset_edit.setFixedWidth(70)
        self.grid_offset_edit.editingFinished.connect(self.change_grid_offset)
        self.status_assist_tool_bar.addWidget(self.grid_offset_edit)

        self.addToolBar(Qt.TopToolBarArea, self.file_tool_bar)
        self.addToolBar(Qt.TopToolBarArea, self.drawing_tool_bar)
        self.addToolBar(Qt.TopToolBarArea, self.layer_tool_bar)
        self.addToolBar(Qt.TopToolBarArea, self.mode_tool_bar)
        self.addToolBar(Qt.TopToolBarArea,self.conversion_tool_bar)
        
        self.addToolBar(Qt.BottomToolBarArea, self.status_assist_tool_bar)
        

    def change_grid_offset(self):
        preferences.grid_offset = self.str_to_float(self.grid_offset_edit.text())


    def str_to_float(self, s):
        result = None
        try:
            result = float(s)
        except:
            pass

        return result


    def polyline_window(self):
        self.create_polyline_window = CreatePolylineWindow(self)
        self.create_polyline_window.create_polyline = self.create_polyline
        self.create_polyline_window.add_point_to_polyline = self.add_point_to_polyline
        self.create_polyline_window.update_polyline_points = self.update_polyline_points
        self.create_polyline_window.remove_window_polyline = self.remove_window_polyline

        self.create_polyline_window.move(self.mapToGlobal(
            QPoint(self.width() / 2, self.height() / 2)
        ))
        self.create_polyline_window.show()
        self.create_polyline_window.create_polyline(QPointF(-0.01, -0.01), QPointF(0.01, 0.01))


    def create_polyline(self, *points):
        self.polyline_from_window = Polyline(*points) 
        self.actual_scene.addItem(self.polyline_from_window)


    def add_point_to_polyline(self, point, radius):
        self.polyline_from_window.add_point(point)
        self.polyline_from_window.create_arc(radius)


    def update_polyline_points(self, points_radii):
        radii = []
        points = points_radii[0]
        if points_radii[1]:
            radii = points_radii[1]

        self.actual_scene.removeItem(self.polyline_from_window)
        self.polyline_from_window = None
        self.create_polyline(*points)
        if radii:
            self.polyline_from_window.create_arcs(*radii)
        self.update()


    def change_mode(self):
        if Line.mode == Item_Mode.Creating:
            Line.mode = Item_Mode.Showing
            Arc.mode = Item_Mode.Showing
        
            for scene in self.scenes:
                for item in scene.items():
                    if isinstance(item, Line):
                        item.setSelected(False)
                        item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                scene.update()
        else:
            Line.mode = Item_Mode.Creating
            Arc.mode = Item_Mode.Creating
            for scene in self.scenes:
                for item in scene.items():
                    if isinstance(item, Line):
                        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                scene.update()
        
        for scene in self.scenes:
            scene.update()


    def remove_window_polyline(self):
        self.actual_scene.removeItem(self.polyline_from_window)
        self.polyline_from_window = None


    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)

        file_menu.addAction(newAct)
        file_menu.addMenu(impMenu)


    def save_project(self):
        ###########################################################

        '''  UWZGLEDNIC POLILINIE!!!!  '''
        
        ##########################################################
        t = QTextEdit()

        for scene in self.scenes:
            t.append('LAYER')
            t.append(scene.name)
            for item in scene.items():
                if isinstance(item, Polyline):
                    t.append('POLYLINE')

                    for point in item.points:
                        t.append('POINT')
                        t.append(str(point.x()))
                        t.append(str(point.y()))

                    for arc in item.arcs:
                        t.append('RADIUS')
                        t.append(str(arc.r))

            t.append('PREVIOUS LAYER ANCHOR')
            if scene.previous_layer_anchor:
                t.append(str(scene.previous_layer_anchor.pos.x))
                t.append(str(scene.previous_layer_anchor.pos.y))
            else:
                t.append(str(None))
                t.append(str(None))

            t.append('NEXT LAYER ANCHOR')
            if scene.next_layer_anchor:
                t.append(str(scene.next_layer_anchor.pos.x))
                t.append(str(scene.next_layer_anchor.pos.y))
            else:
                t.append(str(None))
                t.append(str(None))

            t.append('PREVIOUS LAYER ARC')
            if scene.previous_layer_arc:
                t.append(str(scene.previous_layer_arc.r))
            else:
                t.append(str('None'))

            t.append('NEXT LAYER ARC')
            if scene.next_layer_arc:
                t.append(str(scene.next_layer_arc.r))
            else:
                t.append(str('None'))
        try:
            filename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'))
            with open(filename[0], 'w') as f:
                my_text = t.toPlainText()
                f.write(my_text)
        except:
            pass

    def open_project(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
