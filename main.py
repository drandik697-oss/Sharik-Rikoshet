import sys
import os
import random
from PyQt6 import QtWidgets, QtGui, QtCore

def fix_pix(item):
    item.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)

# меню
class MenuScreen(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_window = parent
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#1e272e"))
        self.setPalette(pal)

        layout = QtWidgets.QVBoxLayout(self)
        
        self.btn_play = self.create_pixel_btn("textures/interface/play.png", self.main_window.start_game)
        self.btn_exit = self.create_pixel_btn("textures/interface/exit.png", QtWidgets.QApplication.instance().quit)
        
        layout.addStretch()
        layout.addWidget(self.btn_play, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_exit, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        bottom = QtWidgets.QHBoxLayout()
        self.mute = False
        self.btn_vol = self.create_pixel_btn("textures/interface/volume_on.png", self.toggle_volume, 1.2)
        self.btn_help = self.create_pixel_btn("textures/interface/help.png", self.main_window.show_rules, 1.2)
        
        bottom.addWidget(self.btn_vol)
        bottom.addStretch()
        bottom.addWidget(self.btn_help)
        layout.addLayout(bottom)

    def create_pixel_btn(self, path, func, scale=2.5): # увеличение кнопок для полного экрана
        btn = QtWidgets.QPushButton()
        if os.path.exists(path):
            pix = QtGui.QPixmap(path)
            pix = pix.scaled(int(pix.width()*scale), int(pix.height()*scale), 
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                             QtCore.Qt.TransformationMode.FastTransformation)
            btn.setIcon(QtGui.QIcon(pix))
            btn.setIconSize(pix.size())
            btn.setFixedSize(pix.size())
            btn.setStyleSheet("border: none; background: transparent;")
        btn.clicked.connect(func)
        return btn

    def toggle_volume(self):
        self.mute = not self.mute
        name = "volume_off.png" if self.mute else "volume_on.png"
        path = f"textures/interface/{name}"
        if os.path.exists(path):
            pix = QtGui.QPixmap(path).scaled(50, 50, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.FastTransformation)
            self.btn_vol.setIcon(QtGui.QIcon(pix))

# игра
class GameScreen(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_window = parent
        
        self.scene = QtWidgets.QGraphicsScene(0, 0, 600, 400)
        self.scene.setBackgroundBrush(QtGui.QColor("#1e272e"))
        
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # удаляем все визуальные ошибки и оптимизируем
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        self.view.setCacheMode(QtWidgets.QGraphicsView.CacheModeFlag.CacheBackground)

        self.ball = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap("textures/Sharik.png"))
        self.paddle = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap("textures/Platforma.png"))
        fix_pix(self.ball)
        fix_pix(self.paddle)
        self.scene.addItem(self.ball)
        self.scene.addItem(self.paddle)

        self.hint_text = QtWidgets.QGraphicsTextItem("Нажмите W")
        self.hint_text.setDefaultTextColor(QtGui.QColor("white"))
        self.hint_text.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        self.scene.addItem(self.hint_text)

        self.active_scancodes = set()
        self.bricks = []
        self.is_ball_launched = False
        self.dx, self.dy = 4, -4
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.game_tick)
        
        self.setup_level()

    # растягивание экрана
    def resizeEvent(self, event):
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def setup_level(self):
        for b in self.bricks: self.scene.removeItem(b)
        self.bricks = []
        for r in range(4):
            for c in range(8):
                idx = random.randint(1, 7)
                brick = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(f"textures/Bricks/brick{idx}.png"))
                brick.hp = 2
                brick.id = idx 
                fix_pix(brick)
                brick.setPos(40 + c * 65, 50 + r * 30)
                self.scene.addItem(brick)
                self.bricks.append(brick)
        
        self.paddle.setPos(250, 370)
        self.reset_ball()
        self.timer.start(16)

    def reset_ball(self):
        self.is_ball_launched = False
        self.hint_text.setPos(220, 200)
        self.hint_text.show()
        self.ball.setPos(self.paddle.x() + self.paddle.pixmap().width()//2 - self.ball.pixmap().width()//2, 
                         self.paddle.y() - self.ball.pixmap().height())

    def game_tick(self):
        step = 8
        x = self.paddle.x()
        
        if not self.is_ball_launched:
            if 17 in self.active_scancodes or QtCore.Qt.Key.Key_W in self.active_scancodes:
                self.is_ball_launched = True
                self.hint_text.hide()
        
        move_left = 30 in self.active_scancodes or QtCore.Qt.Key.Key_Left in self.active_scancodes
        move_right = 32 in self.active_scancodes or QtCore.Qt.Key.Key_Right in self.active_scancodes

        if move_left and x > 0:
            self.paddle.setX(x - step)
        if move_right and x < 600 - self.paddle.pixmap().width():
            self.paddle.setX(x + step)

        if not self.is_ball_launched:
            self.ball.setX(self.paddle.x() + self.paddle.pixmap().width()//2 - self.ball.pixmap().width()//2)
            return

        self.ball.moveBy(self.dx, self.dy)
        p = self.ball.scenePos()
        
        if p.x() <= 0 or p.x() >= 600 - self.ball.pixmap().width(): self.dx = -self.dx
        if p.y() <= 0: self.dy = -self.dy
        
        if self.ball.collidesWithItem(self.paddle) and self.dy > 0:
            self.dy = -self.dy

        for b in self.bricks[:]:
            if self.ball.collidesWithItem(b):
                self.dy = -self.dy
                if b.hp == 2:
                    b.hp = 1
                    pair_idx = 15 - b.id 
                    b.setPixmap(QtGui.QPixmap(f"textures/Bricks/brick{pair_idx}.png"))
                else:
                    self.scene.removeItem(b)
                    self.bricks.remove(b)
                break
        
        if not self.bricks:
            self.timer.stop()
            QtCore.QTimer.singleShot(500, self.setup_level)
        
        if p.y() > 400:
            self.timer.stop()
            self.main_window.back_to_menu()

    def keyPressEvent(self, event):
        self.active_scancodes.add(event.nativeScanCode())
        self.active_scancodes.add(event.key())
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.main_window.showNormal()

    def keyReleaseEvent(self, event):
        self.active_scancodes.discard(event.nativeScanCode())
        self.active_scancodes.discard(event.key())

# главное окно
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Arkanoid")
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.menu = MenuScreen(self)
        self.stack.addWidget(self.menu)
        
        self.showFullScreen()

    def start_game(self):
        self.game = GameScreen(self)
        self.stack.addWidget(self.game)
        self.stack.setCurrentWidget(self.game)
        self.game.setFocus()
        QtCore.QTimer.singleShot(50, lambda: self.game.view.fitInView(self.game.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def show_rules(self):
        self.rules_page = QtWidgets.QWidget()
        self.rules_page.setStyleSheet("background-color: #1e272e; color: white;")
        l = QtWidgets.QVBoxLayout(self.rules_page)
        txt = QtWidgets.QLabel("УПРАВЛЕНИЕ:\n\nA/D или Стрелки\n\nW - Запустить шар\nESC - Оконный режим")
        txt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        btn = QtWidgets.QPushButton("НАЗАД")
        btn.clicked.connect(self.back_to_menu)
        l.addWidget(txt)
        l.addWidget(btn)
        self.stack.addWidget(self.rules_page)
        self.stack.setCurrentWidget(self.rules_page)

    def back_to_menu(self):
        self.stack.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())