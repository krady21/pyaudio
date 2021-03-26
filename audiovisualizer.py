import pyaudio
import wave
import threading
import atexit
import numpy as np
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QCheckBox, QAction, QTabWidget, QMainWindow,
                             QHBoxLayout, QVBoxLayout, QApplication, QStackedWidget, QLabel, QSlider)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtGui, QtCore


class FileAudioRecorder():
    def __init__(self, filename):
        self.wf = wave.open(filename, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  output=True,
                                  stream_callback=self.callback)
        self.plm = 0

    def start(self):
        self.stream.start_stream()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.wf.close()

    def callback(self, data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)


class MicrophoneRecorder(object):
    def __init__(self, rate=4000, chunksize=1024):
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)

        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.fromstring(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames

    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()


class MplFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Proiect Mecatronica"
        self.left = 100
        self.top = 100
        self.width = 1600
        self.height = 1400
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = LiveFFTWidget(self)
        self.setCentralWidget(self.table_widget)
        self.show()


class LiveFFTWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "Offline")
        self.tabs.addTab(self.tab2, "Real Time")

    # customize the UI
    # TAB 1 (offline) - configuration
        # checkboxes normal
        self.boxLowNormal = QCheckBox("Low Frequency", self.tab1)
        self.boxLowNormal.move(50, 750)
        self.boxLowNormal.resize(320, 40)
        self.boxMediumNormal = QCheckBox("Medium Frequency", self.tab1)
        self.boxMediumNormal.move(50, 775)
        self.boxMediumNormal.resize(320, 40)
        self.boxHighNormal = QCheckBox("High Frequency", self.tab1)
        self.boxHighNormal.move(50, 800)
        self.boxHighNormal.resize(320, 40)

        # checkboxes noisy
        self.boxLowNoisy = QCheckBox("Low Frequency", self.tab1)
        self.boxLowNoisy.move(900, 750)
        self.boxLowNoisy.resize(320, 40)
        self.boxMediumNoisy = QCheckBox("Medium Frequency", self.tab1)
        self.boxMediumNoisy.move(900, 775)
        self.boxMediumNoisy.resize(320, 40)
        self.boxHighNoisy = QCheckBox("High Frequency", self.tab1)
        self.boxHighNoisy.move(900, 800)
        self.boxHighNoisy.resize(320, 40)

        # widgets normal 1
        self.bPlayNormal = QPushButton(self.tab1)
        self.bPlayNormal.setText("Play")
        self.bPlayNormal.move(50, 150)
        self.bPlayNormal.resize(120, 35)
        self.bPauseNormal = QPushButton(self.tab1)
        self.bPauseNormal.setText("Pause")
        self.bPauseNormal.move(50, 200)
        self.bPauseNormal.resize(120, 35)
        self.bResumeNormal = QPushButton(self.tab1)
        self.bResumeNormal.setText("Resume")
        self.bResumeNormal.move(50, 250)
        self.bResumeNormal.resize(120, 35)
        self.bLoadNormal = QPushButton(self.tab1)
        self.bLoadNormal.setText("Load")
        self.bLoadNormal.move(50, 300)
        self.bLoadNormal.resize(120, 35)

        # widgets noisy 1
        self.bPlayNoisy = QPushButton(self.tab1)
        self.bPlayNoisy.setText("Play")
        self.bPlayNoisy.move(900, 150)
        self.bPlayNoisy.resize(120, 35)
        self.bPauseNoisy = QPushButton(self.tab1)
        self.bPauseNoisy.setText("Pause")
        self.bPauseNoisy.move(900, 200)
        self.bPauseNoisy.resize(120, 35)
        self.bResumeNoisy = QPushButton(self.tab1)
        self.bResumeNoisy.setText("Resume")
        self.bResumeNoisy.move(900, 250)
        self.bResumeNoisy.resize(120, 35)
        self.bLoadNoisy = QPushButton(self.tab1)
        self.bLoadNoisy.setText("Load")
        self.bLoadNoisy.move(900, 300)
        self.bLoadNoisy.resize(120, 35)

        # widgets normal 2
        self.bSlowerNormal = QPushButton(self.tab1)
        self.bSlowerNormal.setText("Play slower")
        self.bSlowerNormal.move(50, 550)
        self.bSlowerNormal.resize(150, 35)
        self.bFasterNormal = QPushButton(self.tab1)
        self.bFasterNormal.setText("Play faster")
        self.bFasterNormal.move(50, 600)
        self.bFasterNormal.resize(150, 35)
        self.bFFTNormal = QPushButton(self.tab1)
        self.bFFTNormal.setText("FFT Normal")
        self.bFFTNormal.move(50, 650)
        self.bFFTNormal.resize(150, 35)
        self.bSpectNormal = QPushButton(self.tab1)
        self.bSpectNormal.setText("Spectrogram")
        self.bSpectNormal.move(50, 700)
        self.bSpectNormal.resize(150, 35)

        # widgets noisy 2
        self.bSlowerNoisy = QPushButton(self.tab1)
        self.bSlowerNoisy.setText("Play slower")
        self.bSlowerNoisy.move(900, 550)
        self.bSlowerNoisy.resize(150, 35)
        self.bFasterNoisy = QPushButton(self.tab1)
        self.bFasterNoisy.setText("Play faster")
        self.bFasterNoisy.move(900, 600)
        self.bFasterNoisy.resize(150, 35)
        self.bFFTNoisy = QPushButton(self.tab1)
        self.bFFTNoisy.setText("FFT Noisy")
        self.bFFTNoisy.move(900, 650)
        self.bFFTNoisy.resize(150, 35)
        self.bSpectNoisy = QPushButton(self.tab1)
        self.bSpectNoisy.setText("Spectrogram")
        self.bSpectNoisy.move(900, 700)
        self.bSpectNoisy.resize(150, 35)

        # plot normal 1 + caption
        self.labelNormal1 = QLabel("Normal1", self.tab1)
        self.labelNormal1.move(470, 50)
        self.graphNormal1 = pg.PlotWidget(self.tab1)
        self.graphNormal1.move(250, 80)
        self.graphNormal1.resize(500, 350)
        self.graphNormal1.setBackground('w')

        # plot normal 2 + caption
        self.labelNormal2 = QLabel("Normal2", self.tab1)
        self.labelNormal2.move(470, 450)
        self.graphNormal2 = pg.PlotWidget(self.tab1)
        self.graphNormal2.move(250, 480)
        self.graphNormal2.resize(500, 350)
        self.graphNormal2.setBackground('w')

        # plot noisy 1 + caption
        self.labelNoisy1 = QLabel("Noisy1", self.tab1)
        self.labelNoisy1.move(1330, 50)
        self.graphNoisy1 = pg.PlotWidget(self.tab1)
        self.graphNoisy1.move(1100, 80)
        self.graphNoisy1.resize(500, 350)
        self.graphNoisy1.setBackground('w')

        # plot noisy 2 + caption
        self.labelNoisy2 = QLabel("Noisy2", self.tab1)
        self.labelNoisy2.move(1330, 450)
        self.graphNoisy2 = pg.PlotWidget(self.tab1)
        self.graphNoisy2.move(1100, 480)
        self.graphNoisy2.resize(500, 350)
        self.graphNoisy2.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.graphNormal1.plot([0], [0], pen=pen)
        self.graphNormal2.plot([0], [0], pen=pen)
        self.graphNoisy1.plot([0], [0], pen=pen)
        self.graphNoisy2.plot([0], [0], pen=pen)

    # TAB 2 (real time) - configuration
        hbox_gain = QHBoxLayout()
        autoGain = QLabel('Auto gain for frequency spectrum')
        autoGainCheckBox = QCheckBox(checked=True)
        hbox_gain.addWidget(autoGain)
        hbox_gain.addWidget(autoGainCheckBox)

        # reference to checkbox
        self.autoGainCheckBox = autoGainCheckBox

        hbox_fixedGain = QHBoxLayout()
        fixedGain = QLabel('Manual gain level for frequency spectrum')
        fixedGainSlider = QSlider(QtCore.Qt.Horizontal)
        hbox_fixedGain.addWidget(fixedGain)
        hbox_fixedGain.addWidget(fixedGainSlider)
        self.fixedGainSlider = fixedGainSlider

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_gain)
        vbox.addLayout(hbox_fixedGain)

        # mpl figure
        self.main_figure = MplFigure(self)
        vbox.addWidget(self.main_figure.toolbar)
        vbox.addWidget(self.main_figure.canvas)
        self.tab2.setLayout(vbox)
        self.show()

        # timer for callbacks
        timer = QtCore.QTimer()
        timer.timeout.connect(self.handleNewData)
        timer.start(100)

        # keep reference to timer
        self.timer = timer

        # init class data
        self.initData()

        # connect slots
        self.connectSlots()

        # init MPL widget
        self.initMplWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def initData(self):
        mic = MicrophoneRecorder()
        mic.start()

        # keeps reference to mic
        self.mic = mic

        # computes the parameters that will be used during plotting
        self.freq_vect = np.fft.rfftfreq(mic.chunksize,
                                         1./mic.rate)
        self.time_vect = np.arange(
            mic.chunksize, dtype=np.float32) / mic.rate * 1000

    def connectSlots(self):
        pass

    def initMplWidget(self):
        """creates initial matplotlib plots in the main window and keeps
        references for further use"""
        # top plot
        self.ax_top = self.main_figure.figure.add_subplot(211)
        self.ax_top.set_ylim(-32768, 32768)
        self.ax_top.set_xlim(0, self.time_vect.max())
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6)

        # bottom plot
        self.ax_bottom = self.main_figure.figure.add_subplot(212)
        self.ax_bottom.set_ylim(0, 1)
        self.ax_bottom.set_xlim(0, self.freq_vect.max())
        self.ax_bottom.set_xlabel(u'frequency (Hz)', fontsize=6)
        # line objects
        self.line_top, = self.ax_top.plot(self.time_vect,
                                          np.ones_like(self.time_vect))

        self.line_bottom, = self.ax_bottom.plot(self.freq_vect,
                                                np.ones_like(self.freq_vect))

    def handleNewData(self):
        """ handles the asynchroneously collected sound chunks """
        # gets the latest frames
        frames = self.mic.get_frames()

        if len(frames) > 0:
            # keeps only the last frame
            current_frame = frames[-1]
            # plots the time signal
            self.line_top.set_data(self.time_vect, current_frame)
            # computes and plots the fft signal
            fft_frame = np.fft.rfft(current_frame)
            if self.autoGainCheckBox.checkState() == QtCore.Qt.Checked:
                fft_frame /= np.abs(fft_frame).max()
            else:
                fft_frame *= (1 + self.fixedGainSlider.value()) / 5000000.
                # print(np.abs(fft_frame).max())
            self.line_bottom.set_data(self.freq_vect, np.abs(fft_frame))

            # refreshes the plots
            self.main_figure.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())
