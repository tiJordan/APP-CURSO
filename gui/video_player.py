from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QSlider, QMenu
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QIcon
from settings import ICO_PATH, ICON_PLAYER, resource_path
import vlc
import os

def sec_to_str(s):
    s = int(s)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"
    
def centralize_widget(widget):
    qr = widget.frameGeometry()
    cp = widget.screen().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())

class VideoPlayer(QDialog):
    def __init__(self, parent, video_path):
        super().__init__(parent)
        self.setWindowTitle("Player de Vídeo")
        self.setWindowIcon(QIcon(resource_path(ICON_PLAYER)))
        self.setGeometry(200, 120, 950, 560)
        self.video_path = video_path
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(700, 400)
        self.is_fullscreen = False
        centralize_widget(self)
       

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)
        layout.setSpacing(8)

        # Widget de vídeo
        self.video_frame = QWidget(self)
        pal = self.video_frame.palette()
        pal.setColor(QPalette.Window, QColor("black"))
        self.video_frame.setPalette(pal)
        self.video_frame.setAutoFillBackground(True)
        layout.addWidget(self.video_frame, stretch=1)
        

        # Progresso
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)

        # Tempo
        tempo_layout = QHBoxLayout()
        self.label_time = QLabel("00:00 / 00:00")
        tempo_layout.addWidget(self.label_time)
        tempo_layout.addStretch()
        layout.addLayout(tempo_layout)

        # Controles
        ctrl_layout = QHBoxLayout()
        self.play_btn = QPushButton("⏸ Pause")
        self.play_btn.clicked.connect(self.play_pause)
        ctrl_layout.addWidget(self.play_btn)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop)
        ctrl_layout.addWidget(self.stop_btn)
        self.speed_btn = QPushButton("Velocidade: 1x")
        self.speed_btn.clicked.connect(self.open_speed_menu)
        ctrl_layout.addWidget(self.speed_btn)
        self.full_btn = QPushButton("🖵 Tela cheia")
        self.full_btn.clicked.connect(self.toggle_fullscreen)
        ctrl_layout.addWidget(self.full_btn)

        # Volume
        self.vol_icon = QLabel()
        self.vol_icon.setPixmap(QIcon.fromTheme("audio-volume-high").pixmap(24,24))
        ctrl_layout.addWidget(self.vol_icon)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        ctrl_layout.addWidget(self.volume_slider)

        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # VLC setup
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        media = self.instance.media_new(os.path.abspath(self.video_path))
        self.mediaplayer.set_media(media)
        if hasattr(self.mediaplayer, "set_hwnd"):
            self.mediaplayer.set_hwnd(int(self.video_frame.winId()))
        elif hasattr(self.mediaplayer, "set_xwindow"):
            self.mediaplayer.set_xwindow(int(self.video_frame.winId()))
        self.mediaplayer.play()
        self.mediaplayer.audio_set_volume(70)
        self.playing = True
        self.current_speed = 1.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_F11:
                self.toggle_fullscreen()
                return True
            elif event.key() == Qt.Key_Escape and self.is_fullscreen:
                self.toggle_fullscreen()
                return True
        return super().eventFilter(obj, event)

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_btn.setText("▶ Play")
        else:
            self.mediaplayer.play()
            self.play_btn.setText("⏸ Pause")

    def stop(self):
        self.mediaplayer.stop()
        self.close()

    def open_speed_menu(self):
        menu = QMenu(self)
        speeds = [("0.5x", 0.5), ("1x", 1.0),("1,25x", 1.25), ("1.5x", 1.5), ("2x", 2.0)]
        for label, value in speeds:
            act = menu.addAction(label)
            act.triggered.connect(lambda checked, v=value: self.set_speed(v))
        menu.exec_(self.speed_btn.mapToGlobal(self.speed_btn.rect().bottomLeft()))

    def set_speed(self, speed):
        self.current_speed = speed
        try:
            self.mediaplayer.set_rate(speed)
        except:
            pass
        self.speed_btn.setText(f"Velocidade: {speed}x")

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.showFullScreen()
            self.full_btn.setText("🗗 Janela")
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.full_btn.setText("🖵 Tela cheia")
            self.is_fullscreen = False

    def set_position(self, position):
        if self.mediaplayer.get_length() > 0:
            self.mediaplayer.set_position(position / 1000.0)

    def set_volume(self, value):
        self.mediaplayer.audio_set_volume(value)
        if value == 0:
            self.vol_icon.setPixmap(QIcon.fromTheme("audio-volume-muted").pixmap(24,24))
        elif value < 40:
            self.vol_icon.setPixmap(QIcon.fromTheme("audio-volume-low").pixmap(24,24))
        else:
            self.vol_icon.setPixmap(QIcon.fromTheme("audio-volume-high").pixmap(24,24))

    def update_ui(self):
        if self.mediaplayer.get_length() > 0:
            length = self.mediaplayer.get_length() / 1000
            current = self.mediaplayer.get_time() / 1000
            if not self.progress_slider.isSliderDown():
                pos = int((self.mediaplayer.get_position()) * 1000)
                self.progress_slider.setValue(pos)
            self.label_time.setText(f"{sec_to_str(current)} / {sec_to_str(length)}")
        if self.mediaplayer.is_playing():
            self.play_btn.setText("⏸ Pause")
        else:
            self.play_btn.setText("▶ Play")

    def closeEvent(self, event):
        self.mediaplayer.stop()
        event.accept()
