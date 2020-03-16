import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QObject, QRectF, Qt, Signal, Slot,QThread
from PySide2.QtWidgets import QMainWindow,QProgressBar,QPushButton,QGroupBox,QStatusBar,QGridLayout, QFileDialog, QWidget, QLabel,QToolButton,QHBoxLayout,QVBoxLayout
from PySide2.QtGui import QPixmap, QImage, QIcon, QPainter, QPen
import cv2
import os
import time
import glob


from backend.backend_logic import *
from backend.classes import *
# from .backend import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.setGeometry(300,200,500,100)

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)

        selectVideoLabel = QLabel(self.centralWidget)
        selectVideoLabel.setText("Select a video to summarize:")

        self.file_Select_Btn = QPushButton(self.centralWidget)
        self.file_Select_Btn.setGeometry(QtCore.QRect(1082, 80, 121, 28))
        self.file_Select_Btn.setObjectName("file_Select_Btn")
        self.file_Select_Btn.setText("Load Video")

        self.gridLayout.addWidget(selectVideoLabel)

        self.gridLayout.addWidget(self.file_Select_Btn)


        MainWindow.setCentralWidget(self.centralWidget)

        self.statusLabel = QLabel("Loading Video ...")
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)

        self.createStatusBar()


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def createStatusBar(self):
        self.statusBar = QStatusBar()
        self.progressbar.setValue(0)
        self.statusBar.addWidget(self.statusLabel, 1)
        self.statusBar.addWidget(self.progressbar, 2)


class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        Ui_MainWindow.__init__(self)
        QMainWindow.__init__(self)
        # Initialize UI
        self.setWindowTitle('Whiteboard Summarizer')

        # self.createGridLayout()
        # vbox = QVBoxLayout()
        # vbox.addWidget(self.groupBox)
        # self.setLayout(vbox)

        self.setupUi(self)

        # self.setupUi(self)

        self.file_Select_Btn.clicked.connect(self.selectVideo)



    def tr(self, text):
        return QObject.tr(self, text)

    @Slot(str,int)
    def updateStatuBar(self,progress_string,progress_val):
        self.progressbar.setValue(progress_val)
        self.statusLabel.setText(progress_string)

    def selectVideo(self):

        self.path_to_file, _ = QFileDialog.getOpenFileName(self, self.tr("Load Video"), self.tr("~/Desktop/"), self.tr("Images (*.mp4)"),self.tr("Images (*.MTS)"))
        if(self.path_to_file is not None):
            self.setStatusBar(self.statusBar)


            self.backendThread = BackendThread(self.path_to_file )
            self.backendThread.progress_bar.connect(self.updateStatuBar)
            self.backendThread.summarization_result.connect(self.openApp)

            self.backendThread.start()

    def openApp(self,summary_obj_list):
        self.app_window =AppWindow(self.path_to_file,summary_obj_list)
        self.app_window.show()




class BackendThread(QThread):
    progress_bar = Signal(str,int)
    summarization_result = Signal(list)

    def __init__(self, video_path):
        super(BackendThread, self).__init__()
        self.video_path=video_path

    def run(self):
        if split_video_call(self.video_path):
            self.progress_bar.emit("Annotating images ...",30)
            if annotate_call():
                self.progress_bar.emit("Binarizing images ...", 50)

                if binarize_call():
                    self.progress_bar.emit("Creating spatiotemporal groups ...", 65)
                    if spatiotemporal_call():
                        self.progress_bar.emit("Reconstructing and merging ...", 75)
                        if reconstruct_and_merge_call():
                            self.progress_bar.emit("Summarizing images ...", 90)

                            summary_obj_list=summary_call()
                            self.progress_bar.emit("Done ...", 100)
                            self.summarization_result.emit(summary_obj_list)

                        else:
                            print("err3")
                    else:
                        print("err4")
                else:
                    print("err5")
            else:
                print("err6")
        else:
            print("err7")

class Thread(QThread):
    changePixmap = Signal(QImage)

    def __init__(self, image_path):
        super(Thread, self).__init__()
        self.image_path = image_path
        self.play = True
        self.cap = cv2.VideoCapture(self.image_path)
        # frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.sleep_duration = (300 / self.fps)
        self.change_frame_number_flg=False
        self.pause=False
    def run(self):

        while True and self.play:
            # start = time.time()
            while self.pause:
                pass
            if self.change_frame_number_flg:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.new_frame_number))
                print("cap setting inside while")
                self.change_frame_number_flg=False


            ret, frame = self.cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # print(rgbImage.shape)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                # p = convertToQtFormat.scaled(720, 405, Qt.KeepAspectRatio)
                p = convertToQtFormat.scaled(720,405, Qt.KeepAspectRatio)

                self.changePixmap.emit(p)
            self.msleep(self.sleep_duration)

    def stop(self):
        self.play=False
        self.pause=False
        return self.sleep_duration/10
    def change_timestamp(self,timestamp):
        self.new_frame_number=timestamp*self.fps
        print("changing in thread",self.new_frame_number)
        self.change_frame_number_flg=True


class VideoPlayer(QWidget):
    def __init__(self,image_path):
        super().__init__()
        self.title = 'My'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 405
        self.image_path = image_path

        self.initUI()

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(720, 405)
        # create a label
        self.label = QLabel(self)
        self.label.resize(720, 405)

        pLay_pause_btn = QToolButton()
        pLay_pause_btn.setText("Play/Pause")
        pLay_pause_btn.mousePressEvent= self.pauseVideo

        # pLay_pause_btn.setIcon(QIcon(QPixmap("icons/next.png")))
        # next_img_btn.mousePressEvent = self.nextImg

        videoplayer_layout = QVBoxLayout()
        videoplayer_layout.addWidget(self.label)

        play_btn_layout = QHBoxLayout()
        play_btn_layout.addWidget(pLay_pause_btn,Qt.AlignJustify)


        videoplayer_layout.addLayout(play_btn_layout)

        self.setLayout(videoplayer_layout)

        self.th = Thread( self.image_path)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()



        # self.show()

    def closeVideo(self):
        print("close click")

        time.sleep(self.th.stop())

    def pauseVideo(self,event):
        self.th.pause=not self.th.pause



    def load_image(self, frame):
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap().fromImage(qImg)
        # print(pixmap)
        self.scene.addPixmap(pixmap)
        self.view.fitInView(QRectF(0, 0, pixmap.width(), pixmap.height()), Qt.KeepAspectRatio)
        self.scene.update()

    def change_timestamp(self,timestamp):
        self.th.change_timestamp(timestamp)

class SummaryImageScroll(QWidget):
    change_timestamp_signal=Signal(int)
    def __init__(self,summary_obj_list):
        super().__init__()
        self.title = 'Summary Images'
        self.left = 0
        self.top = 0
        self.width = summary_obj_list[0].shape[1]/2
        self.height = summary_obj_list[0].shape[0]/2
        self.summary_obj_list=summary_obj_list
        self.initUI()

    def initUI(self):
        self.img_index=0
        # summary_dir = "/Users/lakshkotian/Documents/ly_pipeline/summary"
        self.pixmap_list=[]

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        self.summary_image_label = QLabel()

        self.loadImg()

        self.summary_image_label.setObjectName("summary_image")
        self.summary_image_label.setGeometry(0,0,self.width ,self.height)
        self.summary_image_label.mousePressEvent = self.getPos
        # self.resize(pixmap.width(), pixmap.height())


        prev_img_btn = QToolButton()
        prev_img_btn.setIcon(QIcon(QPixmap("icons/back.png")))
        prev_img_btn.mousePressEvent= self.prevImg

        next_img_btn = QToolButton()
        next_img_btn.setIcon(QIcon(QPixmap("icons/next.png")))
        next_img_btn.mousePressEvent= self.nextImg

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_img_btn)
        button_layout.addWidget(next_img_btn)
        # button_layout.setAlignment()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.summary_image_label,Qt.AlignLeft|Qt.AlignTop)
        # main_layout.setAlignment(Qt.AlignLeft)
        # main_layout.setAlignment(Qt.AlignTop)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    #
    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.drawPixmap(self.summary_image_label.rect(), self.summary_obj_list[self.img_index].img)
    #     pen = QPen(Qt.red, 2)
    #     painter.setPen(pen)
    #     painter.drawRect(0,0,100,100)
    #     for bndbx in self.summary_obj_list[self.img_index].bndbxes:
    #
    #         painter.drawRect(bndbx[0]/2, bndbx[1]/2, (bndbx[2]-bndbx[0])/2, (bndbx[3]-bndbx[1])/2)

    def getPos(self, event):
        x = event.pos().x()
        y = event.pos().y()

        # print(self.summary_obj_list[self.img_index].bndbxes)
        print([[bndbx[0] / 2, bndbx[1] / 2, bndbx[2] / 2, bndbx[3] / 2] for bndbx in self.summary_obj_list[self.img_index].bndbxes])


        print(self.summary_obj_list[self.img_index].bndbx_timestamps)
        for idx,bndbx in enumerate(self.summary_obj_list[self.img_index].bndbxes):
            if x >= bndbx[0]/2 and x<= bndbx[2]/2 and y >= bndbx[1]/2 and y<= bndbx[3]/2:
                self.change_timestamp_signal.emit(self.summary_obj_list[self.img_index].bndbx_timestamps[idx])
                print(bndbx)
                break
        print(x,y)

        # 517   541  379  472

    def nextImg(self,event):
        self.img_index = (self.img_index+1)%len(self.summary_obj_list)
        self.loadImg()

    def prevImg(self,event):
        self.img_index = (self.img_index-1)%len(self.summary_obj_list)
        print(self.img_index)
        self.loadImg()
    def loadImg(self):
        # self.update()
        # print()
        pixmap = QPixmap(self.summary_obj_list[self.img_index ].img)
        pixmap = pixmap.scaled(self.width, self.height)
        print(pixmap)
        self.summary_image_label.setPixmap(pixmap)


class AppWindow(QWidget):
    def __init__(self,image_path,summary_obj_list):
        super().__init__()
        self.title = 'Video Summarization'
        self.left = 0
        self.top = 0
        self.width = 1440
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.show()

        self.video_player = VideoPlayer(image_path)
        # video_player.show()
        self.summary_scroll_widget = SummaryImageScroll(summary_obj_list)
        self.summary_scroll_widget.change_timestamp_signal.connect(self.change_timestamp)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_player,Qt.AlignVCenter)
        main_layout.addWidget(self.summary_scroll_widget)
        self.setLayout(main_layout)
        print("second show")
        self.show()

    def closeEvent(self, event):
        print("close click")
        self.video_player.closeVideo()
        event.accept()  # let the window close
    @Slot(int)
    def change_timestamp(self,timestamp):
        print("change timestamp called")
        self.video_player.change_timestamp(timestamp)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()