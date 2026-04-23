import sys
from PyQt6 import QtWidgets, QtGui, QtCore

class GameView(QtWidgets.QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)

class MyGame(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моя игра")
        self.setFixedSize(600, 400)
        
        self.scene = QtWidgets.QGraphicsScene(0, 0, 600, 400)

        self.view = GameView(self.scene, self)
        self.view.resize(600, 400)

        # Шарик
        self.ball = QtWidgets.QGraphicsEllipseItem(0, 0, 30, 30)
        self.ball.setBrush(QtGui.QBrush(QtGui.QColor("red")))
        self.scene.addItem(self.ball)
        self.ball.setPos(285, 150)
        self.dx = 3
        self.dy = 3

        # Платформа
        self.paddle = QtWidgets.QGraphicsRectItem(0, 0, 100, 20)
        self.paddle.setBrush(QtGui.QBrush(QtGui.QColor("blue")))
        self.paddle.setPos(250, 370)
        self.scene.addItem(self.paddle)

        # Таймер
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ball)
        self.timer.start(16)

        # Устанавливаем фокус на View
        self.view.setFocus()
        
        self.create_bricks()

    def create_bricks(self): #Кирпичики
        self.bricks = []
        rows = 3
        cols = 5
        brick_width = 80
        brick_height = 25
        gap = 10
        
        total_grid_width = cols * brick_width + (cols - 1) * gap
        start_x = (600 - total_grid_width) // 2
        start_y = 50
        
        for row in range(rows):
            for col in range(cols):
                brick = QtWidgets.QGraphicsRectItem(0, 0, brick_width, brick_height)
                colors = ["#FF5555", "#55FF55", "#5555FF"]
                brick.setBrush(QtGui.QBrush(QtGui.QColor(colors[row])))
                x_pos = start_x + col * (brick_width + gap)
                y_pos = start_y + row * (brick_height + gap)
                brick.setPos(x_pos, y_pos)
                self.scene.addItem(brick)
                self.bricks.append(brick)

    def update_ball(self):
        self.ball.moveBy(self.dx, self.dy)
        pos = self.ball.scenePos()
        
        # Стены и потолок
        if pos.x() <= 0 or pos.x() >= 570:
            self.dx = -self.dx
        if pos.y() <= 0:
            self.dy = -self.dy

        # Платформа
        if self.ball.collidesWithItem(self.paddle) and self.dy > 0:
            self.dy = -self.dy

        # Проверка кирпичей
        for brick in self.bricks[:]:
            if self.ball.collidesWithItem(brick):
                self.scene.removeItem(brick)
                self.bricks.remove(brick)
                self.dy = -self.dy
                
                if not self.bricks:
                    QtCore.QTimer.singleShot(1500, self.create_bricks)
                break

        # Проигрыш
        if pos.y() >= 400:
            self.timer.stop()
            self.ball.setPos(285, 150)
            for b in self.bricks: self.scene.removeItem(b)
            self.create_bricks() 
            QtCore.QTimer.singleShot(1000, self.timer.start)

    def keyPressEvent(self, event):
        x = self.paddle.x()
        step = 30
        key = event.key()
        text = event.text().lower()

        # Управление
        if key == QtCore.Qt.Key.Key_Left or text in ('a', 'ф'):
            if x > 0:
                self.paddle.setX(x - step)
        elif key == QtCore.Qt.Key.Key_Right or text in ('d', 'в'):
            if x < 500:
                self.paddle.setX(x + step)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyGame()
    window.show()
    sys.exit(app.exec())