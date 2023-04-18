import sys
import math

from gui_build import generate_vmf

from PyQt5.QtCore import Qt, QRectF, QPointF, QLine, QSize

from PyQt5.QtGui import (
    QBrush, 
    QPainterPath, 
    QPainter, 
    QColor, 
    QPen, 
    QFont, 
    QIcon)
''' importing main widgets '''
from PyQt5.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QAbstractItemView,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QApplication)
''' importing graphics widgets '''
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem, 
)

font = QFont( 'Lato Light', 9 )
widget_height = 38
length_1, length_2 = 200, 80

def create_line_edit(l, h, text=''):
    line_edit = QLineEdit(text)
    line_edit.setFixedSize(l,h)
    line_edit.setFont( font )
    line_edit.setAlignment( Qt.AlignmentFlag.AlignCenter )
    return line_edit

def create_button(l, h, text):
    button = QPushButton(text)
    button.setFixedSize(l,h)
    button.setFont( font )
    return button

def create_v_layout(item_list, parent=None):
    layout = QVBoxLayout( parent ) if parent else QVBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setAlignment(Qt.AlignTop)

    layout.setSpacing(10)
    for item in item_list:
        if issubclass( item.__class__, QWidget ):
            layout.addWidget( item )
        elif issubclass( item.__class__, QLayout ):
            layout.addLayout( item )
    return layout

def create_h_layout(item_list, parent=None):
    layout = QHBoxLayout( parent ) if parent else QHBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setAlignment(Qt.AlignLeft)

    layout.setSpacing(10)
    for item in item_list:
        if issubclass( item.__class__, QWidget ):
            layout.addWidget( item )
        elif issubclass( item.__class__, QLayout ):
            layout.addLayout( item )
    return layout

class RadioButtonGroup(QWidget):
    def __init__(self, names, parent=None):
        super().__init__(parent)
        self.buttons = [ create_button( 80,38,name) for name in names ]
        self.layout = create_h_layout( self.buttons, parent=self )

    def connect( self, func, cur_item ):
        ''' We need to disconnect all of our buttons first '''
        for b in self.buttons:
            try: b.clicked.disconnect() 
            except Exception: pass
        ''' The stylesheets for handling our radiobuttons '''
        off_style = '''
        QPushButton {
            background-color: #34495e;
            border-radius: 5px;
        }
        QPushButton::hover {
            background-color: #7f8c8d;
            border-radius: 5px;
        }
        '''
        on_style = '''
        QPushButton {
            background-color: #f1c40f;
            border-radius: 5px;
            color: #34495e;
        }
        '''
        def call_and_set_style( cur ):
            func( cur )
            for i,b in enumerate(self.buttons):
                stylesheet = on_style if i == cur else off_style
                b.setStyleSheet( stylesheet )
        
        for i,b in enumerate(self.buttons):
            b.clicked.connect(lambda _, index=i: call_and_set_style(index))
            stylesheet = on_style if i == cur_item else off_style
            b.setStyleSheet( stylesheet )

class ViewMenu(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        ''' Add the Form '''
        self.window = window
        self.lineedit = create_line_edit(length_1, widget_height)
        self.button = create_button(length_2, widget_height,'Add')

        self.form_layout = create_h_layout( [self.lineedit, self.button] )
        self.layout = create_v_layout( [ self.form_layout ], parent=self )

        self.button.clicked.connect( self.add_view_and_item )

    def add_view_and_item( self ):
        def add_view():
            scene = GridScene()
            view = GraphicsView(scene, self.window)
            view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
            # self.window.graphicsViews.append( view )
            self.window.stackedWidget.addWidget( view )
            return view
        
        def add_item(view):
            text = self.lineedit.text()
            self.lineedit.setText('')
            item = ViewMenuItem(text)
            item.button.clicked.connect(lambda _, v=view: self.change_view(v))
            item.remove_button.clicked.connect(lambda _, i=item, v=view: self.remove_view_and_item(i, v))
            self.layout.addWidget(item)
            return item

        view = add_view()
        add_item(view)

    def remove_view_and_item( self, item, view ):
        def remove_view(view):
            self.window.stackedWidget.removeWidget( view )

        def remove_item(item):
            self.layout.removeWidget(item)
            item.deleteLater()
        
        remove_view(view)
        remove_item(item)

    def change_view( self, view ):
        self.window.stackedWidget.setCurrentWidget(view)
        view.setFocus()

class ViewMenuItem(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.button = create_button( length_1, widget_height, text )


        self.remove_button = create_button( length_2, widget_height, 'Remove' )
        self.remove_button.setStyleSheet( open('gui/cssfiles/removestyle.css').read() )

        self.layout = create_h_layout([self.button, self.remove_button], parent=self)

class JumpItemMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.z_rel_lineedit = create_line_edit( length_1, widget_height )
        self.type_radio_buttons = RadioButtonGroup( ['Platform', 'Skip', 'Wallshot', 'Jurf'] )
        self.ramp_radio_buttons = RadioButtonGroup( [ 'flat', '1/2', '2/3', '2/1' ] )
        self.layout = create_v_layout( [self.type_radio_buttons, self.z_rel_lineedit, self.ramp_radio_buttons] ,parent=self )

    def update(self, item):
        self.z_rel_lineedit.setText(str(item.z_max_rel))
        self.type_radio_buttons.connect( item.set_type, item.type )
        self.ramp_radio_buttons.connect( item.set_ramp, item.ramp )

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.font = QFont( 'Lato Light', 8 )
        self.setWindowTitle("Jump Prototyper")
        self.setWindowIcon(QIcon('gui/ui_images/appicon.ico'))
        self.setGeometry( 0,0,1000,800 )

        ''' These handle the views '''
        self.stackedWidget = QStackedWidget()
        self.viewmenu = ViewMenu( self )
        self.jump_item_menu = JumpItemMenu()
        window_items = [
            self.viewmenu,
            self.stackedWidget,
            self.jump_item_menu,
        ]
        self.layout = create_h_layout( window_items, parent=self )

class JumpItem():
    def __init__(self, num, dims, prev ) -> None:
        self.prev = prev
        self.type = num 
        self.z_max_rel = 1
        self.dir, self.normal = 0, 1
        self.dims = dims # x-start, y-start, x-diff, y-diff
        self.ramp = 0 # 0: flat, 1: 1/2

    def set_type(self, type_index):
        self.type = type_index

    def set_ramp(self, ramp_index ):
        self.ramp = ramp_index

    def update_dims( self, dims ):
        self.dims = dims

    def get_z_max( self ):
        if not self.prev:
            return self.z_max_rel
        return self.prev.get_z_max() + self.z_max_rel

class GraphicsRectItem(QGraphicsRectItem):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +10.0
    handleSpace = -5.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, view, color, jump_item, *args):
        """
        Initialize the shape.
        """
        super().__init__(*args)
        
        self.view = view
        self.gridSize = 32
        self.color = color
        self.jump_item = jump_item
        self.dir = 0
        self.status = 0
        self.z_max = 1
        
        self.direction_circles = {}
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()
        self.updateDirectionPos()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.view.window.jump_item_menu.update( self.jump_item )
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)

        """
        Upadate position to fit in grid
        """

        x,y = self.pos().x(), self.pos().y()
        x_div, x_res = divmod(x, self.gridSize)
        y_div, y_res = divmod(y, self.gridSize)
        new_x = x_div * self.gridSize if x_res < self.gridSize/2 else (x_div + 1)*self.gridSize
        new_y = y_div * self.gridSize if y_res < self.gridSize/2 else (y_div + 1)*self.gridSize
        self.setPos( new_x, new_y )

        """
        Update size to fit in grid
        """

        sides = [self.rect().left(), self.rect().top(), self.rect().right(), self.rect().bottom()]
        new_sides = []
        for side in sides:
            side_div, side_res = divmod(side, self.gridSize)
            new_side = side_div * self.gridSize if side_res < self.gridSize/2 else (side_div + 1)*self.gridSize
            new_sides.append(new_side)
        self.setRect( new_sides[0], new_sides[1], new_sides[2]-new_sides[0], new_sides[3]-new_sides[1])
        self.jump_item.update_dims( (
            new_sides[0] + self.pos().x(), 
            new_sides[1] + self.pos().y(), 
            new_sides[2]-new_sides[0], 
            new_sides[3]-new_sides[1] ) )
        self.updateHandlesPos()
        self.updateDirectionPos()


        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right()-s, b.bottom()-s, s, s)

    def updateDirectionPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        direction_dic = {
            0:  QRectF(b.center().x(), b.center().y()-s, s, 2*s),
            1:  QRectF(b.center().x()-s, b.center().y(), 2*s, s),
            2:  QRectF(b.center().x()-s, b.center().y()-s, s, 2*s),
            3:  QRectF(b.center().x()-s, b.center().y()-s, 2*s, s),
        }
        self.direction_circles['dir'] = direction_dic[self.dir]
        self.direction_circles['mid'] = QRectF(b.center().x()-s, b.center().y()-s, 2*s, 2*s)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.updateHandlesPos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor(0, 0, 0), 1.0, Qt.SolidLine))
        painter.drawRect(self.rect())

        """
        Paint the handles in the graphic view.
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for handle, rect in self.handles.items():
            if self.handleSelected is None or handle == self.handleSelected:
                painter.drawRect(rect)

        """
        Paint the direction circle in the graphic view.
        """
        if self.handleSelected is None and self.status == 0:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.direction_circles['mid'])

            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(0, 0, 0, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.direction_circles['dir'])

        if self.handleSelected is None and self.status == 1:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.direction_circles['mid'])

            painter.setRenderHint(QPainter.Antialiasing)
            painter.setFont(QFont('Lato Light', 10))
            painter.drawText( 
                int(self.rect().center().x()-5),
                int(self.rect().center().y()+5),
                str(self.z_max) )

class GridScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect( 0, 0, 640, 640 )
        self.gridSize = 32

        """
        Setting up colors and pens
        """
        self.bg_color = QColor("#ecf0f1")
        self.setBackgroundBrush(self.bg_color)

        self.light_color = QColor("#2c3e50")
        self.light_pen = QPen(self.light_color)
        self.light_pen.setWidth(1)

    def drawBackground(self, painter, rect) -> None:
        super().drawBackground(painter, rect)

        """
        Get the dimensions for our grid
        """
        left, right, top, bottom = (
            int(math.floor(rect.left())), 
            int(math.ceil(rect.right())), 
            int(math.floor(rect.top())), 
            int(math.ceil(rect.bottom())),
        )

        first_left, first_top = left - (left % self.gridSize), top- (top % self.gridSize)

        """
        Construct the crosses
        """
        lines_x, lines_y = [], []
        cross_size = 3
        for x in range( first_left, right, self.gridSize ):
            for y in range( first_top, bottom, self.gridSize ):
                lines_x.append( QLine(x-cross_size, y, x+cross_size, y) )
                lines_y.append( QLine(x, y-cross_size, x ,y+cross_size) )

        painter.setPen( self.light_pen )
        painter.drawLines( *lines_x )
        painter.drawLines( *lines_y )

class GraphicsView(QGraphicsView):
    def __init__(self, scene, window):
        super().__init__()
        self.window = window
        self.scene = scene
        self.cur = None
        self.setScene(scene)
        self.jump_items = []


    def keyPressEvent(self, event):
        dims = (0, 0, 32*2, 32*2)
        if event.key() in { Qt.Key_1, Qt.Key_2, Qt.Key_3 }:
            key_to_num = {
                Qt.Key_1:   0,
                Qt.Key_2:   1,
                Qt.Key_3:   2,
            }
            num_to_color = {
                0:  QColor(255, 0, 0, 100),
                1:  QColor(0, 255, 0, 100),
                2:  QColor(0, 0, 255, 100)
            }
            num = key_to_num[ event.key() ]
            color = num_to_color[ num ]
            jump_item = JumpItem( num, dims, self.cur )
            self.cur = jump_item
            self.jump_items.append( jump_item )
            self.scene.addItem(GraphicsRectItem( self, color, jump_item, *dims))
        
        elif event.key() == Qt.Key_Space:
            generate_vmf(self.jump_items)
            print('COMPILED')
        elif event.key() == Qt.Key_Z:
            for item in self.scene.items():
                item.status = ( item.status + 1 ) % 2
                item.update()
        elif event.key() == Qt.Key_D:
            items = self.scene.selectedItems()
            for item in items:
                item.jump_item.dir = (item.jump_item.dir + 1) % 4
                item.dir = (item.dir + 1) % 4
                item.updateDirectionPos()
                item.update()
        elif event.key() in { Qt.Key_A, Qt.Key_S }:
            for item in self.scene.selectedItems():
                if item.status == 1:
                    key_to_add = {
                        Qt.Key_A:   1,
                        Qt.Key_S:   -1,
                    }
                    item.jump_item.z_max_rel = item.jump_item.z_max_rel + key_to_add[ event.key() ]
                    item.z_max = item.z_max + key_to_add[ event.key() ]
                    item.update()
                    self.window.jump_item_menu.update( item.jump_item )
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('gui/cssfiles/stylesheet.css').read())

    window = MyWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
           