import sys
import base64
import pygame
from mutagen.mp3 import MP3
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QSlider
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap

class MP3Player(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Player")
        self.setGeometry(100, 100, 400, 250)
        self.music_file = None
        self.duration = 0
        self.playing = False
        self.elapsed_time = 0
        self.initial_play = True
        pygame.init()
        pygame.mixer.init()
        self.init_ui()

    def init_ui(self):

        self.btn_load = QPushButton("Load MP3", self)
        self.btn_load.setGeometry(10, 10, 100, 30)
        self.btn_load.clicked.connect(self.load_music)
        self.btn_play_pause = QPushButton("Play", self)
        self.btn_play_pause.setGeometry(120, 10, 100, 30)
        self.btn_play_pause.clicked.connect(self.play_pause_music)
        self.seek_slider = QSlider(Qt.Horizontal, self)
        self.seek_slider.setGeometry(10, 190, 380, 20)
        self.seek_slider.sliderReleased.connect(self.set_timer_value)
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.update_timer)
        self.play_timer_label = QLabel(self)
        self.play_timer_label.setGeometry(12, 220, 200, 20)
        self.play_timer_label.setText("")
        self.remaining_label = QLabel(self)
        self.remaining_label.setGeometry(352, 220, 200, 20)
        self.remaining_label.setText("")
        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 60, 100, 100)
        self.artist_label = QLabel(self)
        self.artist_label.setGeometry(140, 80, 200, 20)
        self.title_label = QLabel(self)
        self.title_label.setGeometry(140, 110, 200, 20)

    def load_music(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open MP3 File", "", "MP3 Files (*.mp3)")
        if filename:
            self.music_file = filename
            self.duration = self.get_duration(filename)
            self.seek_slider.setMaximum(self.duration)
            self.load_metadata(self.music_file)

    def load_metadata(self, mp3_file):
        print(self.music_file)
        mp3_file = self.music_file
        audio = MP3(mp3_file)
        if 'APIC:Cover' in audio.tags:
            cover_image_data = audio.tags['APIC:Cover'].data
            pixmap = QPixmap()
            pixmap.loadFromData(cover_image_data)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)
        if 'TPE1' in audio.tags:
            artist = audio.tags['TPE1'].text[0]
            self.artist_label.setText(artist)
        if 'TIT2' in audio.tags:
            title = audio.tags['TIT2'].text[0]
            self.title_label.setText(title)

    def get_duration(self, filename):
        audio = MP3(filename)
        return int(audio.info.length)

    def play_pause_music(self):
        if not self.playing: 
            if self.initial_play:  
                pygame.mixer.music.load(self.music_file) 
                pygame.mixer.music.play()
                self.initial_play = False 
            else: 
                pygame.mixer.music.unpause()
            self.playing = True
            self.btn_play_pause.setText("Pause")
            self.play_timer.start(1000)  
        elif self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.btn_play_pause.setText("Play")
            self.play_timer.stop()

    def update_timer(self):
        if self.playing:
            self.elapsed_time += 1
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.play_timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            remaining_time = self.duration - self.elapsed_time
            if remaining_time < 0:
                remaining_time = 0
            remaining_minutes = remaining_time // 60
            remaining_seconds = remaining_time % 60
            self.remaining_label.setText(f"{int(remaining_minutes):02d}:{int(remaining_seconds):02d}")
            self.seek_slider.setValue(self.elapsed_time)
            if self.elapsed_time >= self.duration:
                self.play_timer.stop()
                self.btn_play_pause.setText("Play")
                self.playing = False
                pygame.mixer.music.stop()
                self.elapsed_time = 0
                self.seek_slider.setValue(0)
                self.initial_play = True

    def set_timer_value(self):
        slider_position = self.seek_slider.value()
        percentage = slider_position / self.seek_slider.maximum()
        new_timer_value = int(percentage * self.duration)
        self.elapsed_time = new_timer_value
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        self.play_timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        pygame.mixer.music.set_pos(self.elapsed_time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MP3Player()
    player.show()
    sys.exit(app.exec())
