
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowState(QtCore.Qt.WindowFullScreen)  # Full-screen mode
        MainWindow.setStyleSheet("QMainWindow { background-color: #2C2F33; color: #FFFFFF; }")  # Dark theme

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")

        screen_width = QtWidgets.QDesktopWidget().screenGeometry().width()
        screen_height = QtWidgets.QDesktopWidget().screenGeometry().height()

        # Label for device information
        self.deviceInfoLabel = QtWidgets.QLabel(self.centralWidget)
        self.deviceInfoLabel.setGeometry(QtCore.QRect(20, 20, 400, 30))  # Positioned at the top-left
        self.deviceInfoLabel.setObjectName("deviceInfoLabel")
        self.deviceInfoLabel.setStyleSheet("QLabel { font-size: 16px; color: #7289DA; }")
        self.deviceInfoLabel.setText("Device: Camera Model XYZ")

        # Camera feed display with padding and border
        # self.widgetDisplay = QtWidgets.QWidget(self.centralWidget)
        # self.widgetDisplay.setGeometry(QtCore.QRect(10, 80, 2048, 512))  # Increased vertical position to add gap
        # self.widgetDisplay.setObjectName("widgetDisplay")
        # self.widgetDisplay.setStyleSheet("background-color: #000000; border: 5px solid #4CAF50; padding: 10px;")  # Added border and padding

        

        # Camera feed display with padding and border
        self.widgetDisplay = QtWidgets.QWidget(self.centralWidget)
        
        # Dynamically calculate the width and height based on the screen size
        feed_width = screen_width - 50  # Adjust to leave some margin from the right
        feed_height = int(feed_width * (512 / 2048))  # Maintain the aspect ratio
        
        # Set geometry: starting from position (10, 80) and dynamically adjusted size
        self.widgetDisplay.setGeometry(QtCore.QRect(10, 80, feed_width+30, feed_height))
        self.widgetDisplay.setObjectName("widgetDisplay")
        self.widgetDisplay.setStyleSheet("background-color: #000000; border: 5px solid #4CAF50; padding: 10px;")  # Added border and padding

        # Buttons for control
        self.bnStart = QtWidgets.QPushButton(self.centralWidget)
        self.bnStart.setGeometry(QtCore.QRect(300, 20, 125, 40))  # Positioned at the top-right
        self.bnStart.setObjectName("bnStart")
        self.bnStart.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; border: none; border-radius: 4px; }"
                                    "QPushButton:disabled { background-color: #808080; }")
        self.bnStart.setText("Start Acquisition")

        self.bnStop = QtWidgets.QPushButton(self.centralWidget)
        self.bnStop.setGeometry(QtCore.QRect(450, 20, 125, 40))  # Positioned next to Start button
        self.bnStop.setObjectName("bnStop")
        self.bnStop.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-size: 14px; padding: 10px; border: none; border-radius: 4px; }"
                                   "QPushButton:disabled { background-color: #808080; }")
        self.bnStop.setText("Stop Acquisition")

        self.bnRefresh = QtWidgets.QPushButton(self.centralWidget)
        self.bnRefresh.setGeometry(QtCore.QRect(600, 20, 100, 40))  # Positioned next to Stop button
        self.bnRefresh.setObjectName("bnRefresh")
        self.bnRefresh.setStyleSheet("QPushButton { background-color: #1E90FF; color: white; font-size: 14px; padding: 10px; border: none; border-radius: 4px; }"
                                      "QPushButton:hover { background-color: #1C86EE; }")
        self.bnRefresh.setText("Refresh")

        self.bnExit = QtWidgets.QPushButton(self.centralWidget)
        self.bnExit.setGeometry(QtCore.QRect(750, 20, 80, 40))  # Positioned next to Refresh button
        self.bnExit.setObjectName("bnExit")
        self.bnExit.setStyleSheet("QPushButton { background-color: #FF6347; color: white; font-size: 14px; padding: 10px; border: none; border-radius: 4px; }"
                                   "QPushButton:hover { background-color: #FF4500; }")
        self.bnExit.setText("Exit")

        # Adjust layout and remove unnecessary space
        MainWindow.setCentralWidget(self.centralWidget)

        # Status bar
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        self.statusBar.setStyleSheet("QStatusBar { font-size: 12px; color: #FFFFFF; }")
        MainWindow.setStatusBar(self.statusBar)

        # Connect Exit button to close the application
        self.bnExit.clicked.connect(MainWindow.close)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Modern Camera Viewer"))
