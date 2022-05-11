from copy import copy
import os
from os import scandir
import sys
from tkinter.font import BOLD
import unicodedata

import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl, QFileInfo, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection


from sound_functions import *
from conf import *

class MainMenu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.interface()

    def interface(self):
        self.resize(SIZE, SIZE)

        title = QLabel('Projekt 1', self)
        title.setFont(QFont('Peyo', 30))
        title.setAlignment(QtCore.Qt.AlignCenter)

        info_button = QLabel('Kliknij imię osoby, której nagrania chcesz przeanalizować', self)
        info_button.setFont(QFont('Arial', 15))
        info_button.setAlignment(QtCore.Qt.AlignCenter)


        button_maciej = QPushButton('Maciej', self)
        button_maciej.setFont(QFont('Arial', 10))
        button_dawid = QPushButton('Dawid', self)
        button_dawid.setFont(QFont('Arial', 10))
        button_others = QPushButton('Others', self)
        button_others.setFont(QFont('Arial', 10))

        button_maciej.clicked.connect(self.on_button_clicked_maciej)
        button_dawid.clicked.connect(self.on_button_clicked_dawid)
        button_others.clicked.connect(self.on_button_clicked_others)


        button_layout = QGridLayout()
        button_layout.addWidget(button_maciej, 0, 0, alignment=QtCore.Qt.AlignTop)
        button_layout.addWidget(button_dawid, 0, 1, alignment=QtCore.Qt.AlignTop)
        button_layout.addWidget(button_others, 0, 2, alignment=QtCore.Qt.AlignTop)

        button_exit = QPushButton('Exit', self)
        button_exit.clicked.connect(app.exit)
        exit_layout = QHBoxLayout()
        exit_layout.addStretch(7)
        exit_layout.addWidget(button_exit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title, alignment=QtCore.Qt.AlignBottom)
        main_layout.addWidget(info_button, alignment=QtCore.Qt.AlignBottom)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(exit_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Analiza dźwięku')
        self.setWindowIcon(QIcon('./pngs/analyze-sound-wave.png'))
        self.show()

    def on_button_clicked_maciej(self):
        self.dialog = PlotMenu('Maciej')
        self.close()
        self.dialog.show()

    def on_button_clicked_dawid(self):
        self.dialog = PlotMenu('Dawid')
        self.close()
        self.dialog.show()
    def on_button_clicked_others(self):
        self.dialog = PlotMenu('Others')
        self.close()
        self.dialog.show()


class PlotMenu(QWidget):
    def __init__(self, imie = 'Maciej', parent = None):
        super().__init__(parent)
        self.imie = imie

        self.resize(SIZE, SIZE)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.tabs = QTabWidget()

        self.plot()
        self.features()
        self.frequency_plot()

        self.layout.addWidget(self.tabs)

        self.setWindowTitle('Analiza dźwięku')
        self.setWindowIcon(QIcon('./pngs/analyze-sound-wave.png'))
        self.show()

    def frequency_plot(self):

        self.main_frequency_plot = QWidget()
        self.main_frequency_plot_layout = QGridLayout()

        self.main_frequency_plot_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'BE'), 0, 0)
        self.main_frequency_plot.setLayout(self.main_frequency_plot_layout)

        self.tabs.addTab(self.main_frequency_plot, 'Frequency plot')

    def plot(self):

        self.choose_file = QComboBox()
        if self.imie == 'Maciej':
            self.choose_file.addItems(all_filenames_m)
        if self.imie == 'Dawid':
            self.choose_file.addItems(all_filenames_d)
        if self.imie == 'Others':
            self.choose_file.addItems(all_filenames_o)

        self.main_plot = QWidget()
        self.main_plot_layout = QGridLayout()

        self.plot_generate()

        self.choose_file.activated.connect(self.generate_plots_statistics)


        self.slider_widget = QWidget()
        self.slider_layer = QGridLayout()

        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_min.setMinimum(10)
        self.slider_min.setMaximum(3000)
        self.slider_min.setValue(100)
        self.slider_min.setTickInterval(50)
        self.slider_min.setTickPosition(QSlider.TicksBelow)

        self.slider_width = QSlider(Qt.Horizontal)
        self.slider_width.setMinimum(10)
        self.slider_width.setMaximum(3000)
        self.slider_width.setValue(100)
        self.slider_width.setTickInterval(50)
        self.slider_width.setTickPosition(QSlider.TicksBelow)

        self.slider_min.valueChanged.connect(self.generate_plots_statistics)
        self.slider_width.valueChanged.connect(self.generate_plots_statistics)
        self.slider_min.valueChanged.connect(self.updateLabel_min)
        self.slider_width.valueChanged.connect(self.updateLabel_width)


        self.slider_min_l = QLabel('100', self)
        self.slider_min_l.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.slider_width_l = QLabel('100', self)
        self.slider_width_l.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.slider_min_label = QLabel('Ustawienie f0 dla Band Energy')
        self.slider_min_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.slider_width_label = QLabel('Ustawienie długości przedziału dla Band Energy')
        self.slider_width_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)


        self.slider_layer.addWidget(self.slider_min_label, 0, 0)
        self.slider_layer.addWidget(self.slider_width_label, 0, 1)

        self.slider_layer.addWidget(self.slider_min, 1, 0)
        self.slider_layer.addWidget(self.slider_width, 1, 1)

        self.slider_layer.addWidget(self.slider_min_l, 2, 0)
        self.slider_layer.addWidget(self.slider_width_l, 2, 1)

        self.slider_widget.setLayout(self.slider_layer)

        button_back = QPushButton('Back', self)
        button_back.clicked.connect(self.go_back)
        self.back_layout = QHBoxLayout()

        self.music_play = QPushButton('Play', clicked = self.play_audio_file)
        self.volume_up = QPushButton('+', clicked = self.volume_up)
        self.volume_down = QPushButton('-', clicked = self.volume_down)
        self.player = QMediaPlayer()

        self.back_layout.addWidget(self.choose_file)
        self.back_layout.addWidget(self.slider_widget)
        self.back_layout.addWidget(self.volume_up)
        self.back_layout.addWidget(self.music_play)
        self.back_layout.addWidget(self.volume_down)


        self.back_layout.addWidget(button_back)

        self.main_plot_layout.addLayout(self.back_layout, 1, 0)

        self.main_plot.setLayout(self.main_plot_layout)
        self.tabs.addTab(self.main_plot, 'Waveform')

    def updateLabel_min(self, value):
        self.slider_min_l.setText(str(value))

    def updateLabel_width(self, value):
        self.slider_width_l.setText(str(value))

    def volume_up(self):
        current_volume = self.player.volume()
        print(current_volume)
        self.player.setVolume(current_volume + 5)

    def volume_down(self):
        current_volume = self.player.volume()
        print(current_volume)
        self.player.setVolume(current_volume - 5)

    def play_audio_file(self):
        if self.imie == 'Maciej':
            path = './samples/Maciej_Chylak/Znormalizowane/' + str(self.choose_file.currentText())
        elif self.imie == 'Dawid':
            path = './samples/Dawid_Janus/Znormalizowane/' + str(self.choose_file.currentText())
        elif self.imie == 'Others':
            path = './samples/Others/' + str(self.choose_file.currentText())

        url = QUrl.fromLocalFile(QFileInfo(path).absoluteFilePath())
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()

    def plot_generate(self):
        self.plot_toolbar_widget = QWidget()
        self.plot_toolbar_layout = QGridLayout()
        self.sc, self.toolbar = self.waveform(str(self.choose_file.currentText()))

        self.plot_toolbar_layout.addWidget(self.toolbar, 0, 0)
        self.plot_toolbar_layout.addWidget(self.sc, 1, 0)
        self.plot_toolbar_widget.setLayout(self.plot_toolbar_layout)

        self.main_plot_layout.addWidget(self.plot_toolbar_widget, 0, 0)

    def features(self):

        self.main_features = QWidget()
        self.main_features_layout = QGridLayout()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.frame_statistics()
        self.main_features_layout.addWidget(line, 1, 0)
        #self.clip_statistics()

        self.main_features.setLayout(self.main_features_layout)
        self.tabs.addTab(self.main_features, 'Features')

    def frame_statistics(self):
        self.frame = QWidget()
        self.frame_layout = QGridLayout()

        frame_title = QLabel()
        frame_title.setText('Features related with frame')
        frame_title.setAlignment(QtCore.Qt.AlignCenter)
        frame_title.setFont(QFont('Arial', 20))

        self.frame_layout.addWidget(frame_title, 0, 0, 1, 0)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'Volume'), 1, 0)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'BW'), 1, 1)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'FC'), 2, 0)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'BE'), 2, 1)
        #self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'BER'), 3, 0)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'SFM'), 3, 0)
        self.frame_layout.addWidget(self.plot_of_feature(self.choose_file.currentText(), 'SCF'), 3, 1)
        self.frame.setLayout(self.frame_layout)

        self.main_features_layout.addWidget(self.frame, 0, 0)

    def clip_statistics(self):
        self.clip = QWidget()
        self.clip_layout = QGridLayout()
        clip_title = QLabel()
        clip_title.setText('Features related with clip')
        clip_title.setAlignment(QtCore.Qt.AlignCenter)
        clip_title.setFont(QFont('Arial', 20))

        self.clip_layout.addWidget(clip_title, 4, 0, 1, 0)
        self.clip_layout.addWidget(self.label_element('VSTD', VSTD, self.choose_file.currentText(), False), 5, 0)
        self.clip_layout.addWidget(self.label_element('VDR', volume_dynamic_range, self.choose_file.currentText(), False), 5, 1)
        self.clip_layout.addWidget(self.label_element('IS MUSIC?', is_music, self.choose_file.currentText(), False), 5, 2)
        self.clip_layout.addWidget(self.label_element('LSTER', low_short_time_energy_ratio, self.choose_file.currentText(), False), 6, 0)
        self.clip_layout.addWidget(self.label_element('ZSTD', standard_deviation_of_zcr, self.choose_file.currentText(), False), 6, 1)
        self.clip_layout.addWidget(self.label_element('HZCRR', high_zero_crossing_rate_ratio, self.choose_file.currentText(), False), 6, 2)
        self.clip_layout.addWidget(self.label_element('Energy Entropy', energy_entropy, self.choose_file.currentText(), False, 100), 7, 0, 1, 3)
        self.clip.setLayout(self.clip_layout)

        self.main_features_layout.addWidget(self.clip, 2, 0)

    def label_element(self, text, function, filename, frame = True, K = -1):
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel()
        label.setText(text)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QFont('Arial', 12, weight=100))

        output = QLabel()
        if not frame and K == -1:
            output.setText(str(function(filename, self.imie)))
        elif K != -1:
            output.setText(str(function(filename, self.imie, K)))
        output.setAlignment(QtCore.Qt.AlignCenter)
        output.setFont(QFont('Arial', 8))

        layout.addWidget(label, alignment=QtCore.Qt.AlignBottom)
        layout.addWidget(output, alignment=QtCore.Qt.AlignTop)

        widget.setLayout(layout)

        return widget

    def generate_plots_statistics(self, _):

        self.main_plot_layout.removeWidget(self.plot_toolbar_widget)
        self.plot_generate()

        self.main_features_layout.removeWidget(self.frame)
        self.frame_statistics()

        #self.main_features_layout.removeWidget(self.clip)
        #self.clip_statistics()


    def waveform(self, filename):
        samplerate , data = read_wav_clip(filename, self.imie)
        length = len(data) / samplerate
        time = np.linspace(0, length, len(data))
        sc = MplCanvas(self, width=5, height=4, dpi=100)

        pomoc0 = copy(time)
        pomoc05 = copy(time)
        pomoc1= copy(time)

        x = self.color_silence(filename, self.imie)

        for i in range(len(time)):
            if x[i]==1:
                pomoc0[i]=None
                pomoc05[i]=None
            elif  x[i]==0.5:
                pomoc1[i]=None
                pomoc0[i]=None
            else:
                pomoc1[i]=None
                pomoc05[i]=None

        sc.axes.plot(pomoc0, data, c='black', label='silcence')
        sc.axes.legend()
        if self.imie != 'Others':
            sc.axes.plot(pomoc05, data, c='green', label='voiceless')
            sc.axes.legend()
        sc.axes.plot(pomoc1, data, c='blue', label='voice')
        sc.axes.legend()

        toolbar = NavigationToolbar(sc, self)

        return sc, toolbar

    def plot_of_feature(self, filename,  feature_name):

        plot_label = QLabel()
        if feature_name == 'Volume':
            y = volume2(filename, self.imie)
            plot_label.setText('Volume')
        if feature_name == 'BW':
            y = BW(filename, self.imie)
            plot_label.setText('Bandwidth')
        if feature_name == 'FC':
            y =  FC(filename, self.imie)
            plot_label.setText('Frequency Centroid')
        if feature_name == 'BE':
            min = int(self.slider_min_l.text())
            width = int(self.slider_width_l.text())
            y = BE(filename, self.imie, min, min + width)
            plot_label.setText('Band Energy')
        if feature_name == 'BER':
            y = BER(filename, self.imie, 10, 200)
            plot_label.setText('Band Energy Ratio')
        if feature_name == 'SFM':
            y = spectral_flatness_measure(filename, self.imie)
            plot_label.setText('Spectral Flatness Measure')
        if feature_name == 'SCF':
            y = spectral_crest_factor(filename, self.imie)
            plot_label.setText('Spectral Crest Factor')
        if feature_name == 'Frequenct plot':
            y = spectral_crest_factor(filename, self.imie)
            plot_label.setText('Frequency plot')

        plot_label.setAlignment(QtCore.Qt.AlignCenter)
        plot_label.setFont(QFont('Arial', 12, weight=100))

        time = np.linspace(1, len(y), len(y))
        sc = MplCanvas(self, width=2, height=3, dpi=100)

        sc.axes.plot(time, y)

        toolbar = NavigationToolbar(sc, self)

        plot_toolbar_widget = QWidget()
        plot_toolbar_layout = QGridLayout()

        plot_toolbar_layout.addWidget(plot_label, 0, 0)
        plot_toolbar_layout.addWidget(toolbar, 1, 0)
        plot_toolbar_layout.addWidget(sc, 2, 0)
        plot_toolbar_widget.setLayout(plot_toolbar_layout)

        return plot_toolbar_widget

    def color_silence(self, filename, imie):

        samplerate, data = read_wav(filename,imie)
        list_of_silence = []
        list_of_silent_frame = silent_voiceless_ratio(filename,imie)
        for i,ramka in enumerate(data):
            pomocnicza=list_of_silent_frame[i]
            for j in range(len(ramka)):
                list_of_silence.append(pomocnicza)

        return list_of_silence

    def go_back(self):
        self.back = MainMenu()
        self.close()
        self.back.show()

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_menu = MainMenu()
    sys.exit(app.exec_())
