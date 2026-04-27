import sys
import os
import random
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

def fix_pix(item):
    item.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)

# экран окончания игры
class GameOverScreen(QtWidgets.QWidget):
    def __init__(self, parent, final_score):
        super().__init__()
        self.main_window = parent
        self.setStyleSheet("background-color: #1e272e; color: white;")
        layout = QtWidgets.QVBoxLayout(self)
        
        title = QtWidgets.QLabel("Игра окончена!")
        title.setFont(QtGui.QFont("Segoe UI", 32, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        score_lbl = QtWidgets.QLabel(f"Ваши очки: {final_score}")
        score_lbl.setFont(QtGui.QFont("Segoe UI", 20))
        score_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        btn_menu = QtWidgets.QPushButton("Главное меню")
        btn_menu.setFixedSize(250, 60)
        btn_menu.setStyleSheet("""
            QPushButton {
                border: 3px solid black;
                background: transparent;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        btn_menu.clicked.connect(self.main_window.back_to_menu)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(score_lbl)
        layout.addSpacing(40)
        layout.addWidget(btn_menu, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

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

    def create_pixel_btn(self, path, func, scale=2.5):
        btn = QtWidgets.QPushButton()
        if os.path.exists(path):
            pix = QtGui.QPixmap(path)
            pix = pix.scaled(int(pix.width()*scale), int(pix.height()*scale), 
                             QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                             QtCore.Qt.TransformationMode.FastTransformation)
            btn.setIcon(QtGui.QIcon(pix))
            btn.setIconSize(pix.size())
            btn.setFixedSize(pix.width() + 10, pix.height() + 10)
            btn.setStyleSheet("""
                QPushButton { border: 3px solid transparent; background: transparent; padding: 2px; }
                QPushButton:hover { border: 3px solid black; border-radius: 8px; }
            """)
        btn.clicked.connect(func)
        return btn

    def toggle_volume(self):
        audio = self.main_window.audio_output
        
        if not self.mute:
            audio.setVolume(0)
            self.mute = True
            self.btn_vol.setIcon(QtGui.QIcon("textures/interface/volume_off.png"))
        else:
            audio.setVolume(0.5)
            self.mute = False
            self.btn_vol.setIcon(QtGui.QIcon("textures/interface/volume_on.png"))

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
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.ball = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap("textures/Sharik.png"))
        self.paddle = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap("textures/Platforma.png"))
        
        fix_pix(self.ball)
        fix_pix(self.paddle)
  
        b_rect = self.ball.boundingRect()
        self.ball.setTransformOriginPoint(b_rect.width()/2, b_rect.height()/2)
        
        self.scene.addItem(self.ball)
        self.scene.addItem(self.paddle)

        self.hint_text = QtWidgets.QGraphicsTextItem("Нажмите W")
        self.hint_text.setDefaultTextColor(QtGui.QColor("white"))
        self.hint_text.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Weight.Bold))
        self.scene.addItem(self.hint_text)

        self.score = 0
        self.score_text = QtWidgets.QGraphicsTextItem(f"Очки: {self.score}")
        self.score_text.setDefaultTextColor(QtGui.QColor("white"))
        self.score_text.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Weight.Bold))
        self.score_text.setPos(460, 365) 
        self.scene.addItem(self.score_text)

        self.active_scancodes = set()
        self.bricks = []
        self.is_ball_launched = False
        self.dx, self.dy = 4, -4
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.game_tick)
        
        self.setup_level()

    def resizeEvent(self, event):
        self.view.setGeometry(0, 0, self.width(), self.height())
        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def setup_level(self):
        for b in self.bricks: 
            if b.scene(): self.scene.removeItem(b)
        self.bricks = []
        self.score_text.setPlainText(f"Очки: {self.score}")
        
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

        if move_left and x > 0: self.paddle.setX(x - step)
        if move_right and x < 600 - self.paddle.pixmap().width(): self.paddle.setX(x + step)

        if not self.is_ball_launched:
            self.ball.setX(self.paddle.x() + self.paddle.pixmap().width()//2 - self.ball.pixmap().width()//2)
            return

        self.ball.setRotation(self.ball.rotation() + 3)
        self.ball.moveBy(self.dx, self.dy)
        
        p = self.ball.scenePos()
        ball_w = self.ball.pixmap().width()

        # границы
        if p.x() <= 0:
            self.dx = abs(self.dx)
        elif p.x() >= 600 - ball_w:
            self.dx = -abs(self.dx)
            
        if p.y() <= 0:
            self.dy = abs(self.dy)

        # платформа
        if self.ball.collidesWithItem(self.paddle) and self.dy > 0:
            self.dy = -abs(self.dy)

        # кирпичи
        for b in self.bricks[:]:
            if self.ball.collidesWithItem(b):
                self.dy = -self.dy
                if b.hp == 2:
                    b.hp = 1
                    self.score += 1
                    b.setPixmap(QtGui.QPixmap(f"textures/Bricks/brick{15 - b.id}.png"))
                else:
                    self.score += 3
                    self.scene.removeItem(b)
                    self.bricks.remove(b)
                self.score_text.setPlainText(f"Очки: {self.score}")
                break

        if not self.bricks:
            self.timer.stop()
            QtCore.QTimer.singleShot(500, self.setup_level)
        
        if p.y() > 400:
            self.timer.stop()
            self.main_window.show_game_over(self.score)
            
    def keyPressEvent(self, event):
        self.active_scancodes.add(event.nativeScanCode())
        self.active_scancodes.add(event.key())
        if event.key() == QtCore.Qt.Key.Key_Escape: self.main_window.showNormal()

    def keyReleaseEvent(self, event):
        self.active_scancodes.discard(event.nativeScanCode())
        self.active_scancodes.discard(event.key())

# главное меню
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile("bg_music.mp3"))
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.audio_output.setVolume(0.5)
        self.player.play()
        self.setWindowTitle("Sharik-Rikoshet")
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

    def show_game_over(self, score):
        self.over_screen = GameOverScreen(self, score)
        self.stack.addWidget(self.over_screen)
        self.stack.setCurrentWidget(self.over_screen)

    def show_rules(self):
        self.rules_page = QtWidgets.QWidget()
        self.rules_page.setStyleSheet("background-color: #1e272e; color: white;")
        layout = QtWidgets.QVBoxLayout(self.rules_page)
        title = QtWidgets.QLabel("ПРАВИЛА ИГРЫ")
        title.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        rules_text = (
            "У пользователя есть шарик, кирпичи, платформа и счётчик очков. "
            "Шарик может отскакивать буквально от всего, но, чтобы управлять "
            "направлением его полета, у игрока есть платформа внизу игрового экрана. "
            "Задача игрока: набрать как можно больше очков путем разбивания кирпичиков.\n\n"
            "Управление: A, D или Стрелки - движение; W - запуск мяча; Esc - выход из Fullscreen."
        )
        content = QtWidgets.QLabel(rules_text)
        content.setWordWrap(True)
        content.setFont(QtGui.QFont("Arial", 12))
        content.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
        
        btn = QtWidgets.QPushButton("НАЗАД")
        btn.setFixedSize(100, 40)
        btn.setStyleSheet("background-color: #34495e; border: none; border-radius: 5px;")
        btn.clicked.connect(self.back_to_menu)
        
        layout.addWidget(title)
        layout.addWidget(content)
        layout.addWidget(btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.rules_page)
        self.stack.setCurrentWidget(self.rules_page)

    def back_to_menu(self):
        self.stack.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())