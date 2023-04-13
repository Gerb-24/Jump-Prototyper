import sys
import math

from gui_build import generate_vmf

from PyQt5.QtCore import Qt, QRectF, QPointF, QLine
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem

class JumpItem():
    def __init__(self, num, dims ) -> None:
        self.num = num
        self.dir = 0
        self.dims = dims # x-start, y-start, x-diff, y-diff
    def update_dims( self, dims ):
        self.dims = dims

class GraphicsRectItem(QGraphicsRectItem):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

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

    def __init__(self, color, jump_item, *args):
        """
        Initialize the shape.
        """
        super().__init__(*args)
        
        self.gridSize = 32
        self.color = color
        self.jump_item = jump_item
        self.dir = 0
        
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
        if self.handleSelected is None:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.direction_circles['mid'])

            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(0, 0, 0, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.direction_circles['dir'])

class GridScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
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
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.setScene(scene)
        self.jump_items = []

    def keyPressEvent(self, event):
        dims = (0, 0, 32*2, 32*2)
        if event.key() in { Qt.Key_1, Qt.Key_2, Qt.Key_3 }:
            key_to_num = {
                Qt.Key_1:   1,
                Qt.Key_2:   2,
                Qt.Key_3:   3,
            }
            num_to_color = {
                1:  QColor(255, 0, 0, 100),
                2:  QColor(0, 255, 0, 100),
                3:  QColor(0, 0, 255, 100)
            }
            num = key_to_num[ event.key() ]
            color = num_to_color[ num ]
            jump_item = JumpItem( num, dims )
            self.jump_items.append( jump_item )
            self.scene.addItem(GraphicsRectItem(color, jump_item, *dims))
        
        elif event.key() == Qt.Key_Space:
            generate_vmf(self.jump_items)
            print('COMPILED')
        elif event.key() == Qt.Key_D:
            items = self.scene.selectedItems()
            for item in items:
                item.jump_item.dir = (item.jump_item.dir + 1) % 4
                item.dir = (item.dir + 1) % 4
                item.updateDirectionPos()
                item.update()
        else:
            super().keyPressEvent(event)


def main():

    app = QApplication(sys.argv)

    
    scene = GridScene()
    scene.setSceneRect(0, 0, 640, 640)

    grview = GraphicsView(scene)

    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
           