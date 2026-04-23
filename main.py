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

    def update_ball(self):
        self.ball.moveBy(self.dx, self.dy)
        pos = self.ball.scenePos()
        
        if pos.x() <= 0 or pos.x() >= 570:
            self.dx = -self.dx
        if pos.y() <= 0:
            self.dy = -self.dy

        if self.ball.collidesWithItem(self.paddle) and self.dy > 0:
            self.dy = -self.dy

        if pos.y() >= 400:
            self.timer.stop()
            self.ball.setPos(285, 150)
            QtCore.QTimer.singleShot(1000, self.timer.start)

    def keyPressEvent(self, event):
        x = self.paddle.x()
        step = 30
        key = event.key()
        text = event.text().lower()

        # Проверяем код клавиши
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