# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 700)
        
        # ================= 美化核心：全局 QSS 样式表 (暗黑主题) =================
        MainWindow.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 6px;
                padding: 6px 10px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #a6adc8;
            }
            QTableWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                gridline-color: #45475a;
                outline: 0;
            }
            QTableWidget::item:selected {
                background-color: #585b70;
                color: #a6e3a1;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #cdd6f4;
                padding: 6px;
                border: none;
                border-right: 1px solid #45475a;
                border-bottom: 1px solid #45475a;
                font-weight: bold;
            }
            QTextBrowser {
                background-color: #11111b;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                color: #a6e3a1;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ================= 1. 主垂直布局 =================
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(15)

        # ================= 2. 顶部输入区 (网格布局) =================
        self.top_grid = QtWidgets.QGridLayout()
        self.top_grid.setVerticalSpacing(15)
        self.top_grid.setHorizontalSpacing(10)

        # 第一行：视频路径
        self.label_url = QtWidgets.QLabel("输入视频路径", self.centralwidget)
        self.Input_url = QtWidgets.QLineEdit(self.centralwidget)
        self.Input_url.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.top_grid.addWidget(self.label_url, 0, 0)
        self.top_grid.addWidget(self.Input_url, 0, 1, 1, 2) # 占据两列

        # 第二行：Cookie
        self.label_cookie = QtWidgets.QLabel("选择 Cookie", self.centralwidget)
        self.Input_cookie = QtWidgets.QLineEdit(self.centralwidget)
        self.Input_cookie.setText("www.youtube.com_cookies.txt")
        self.c_find_button = QtWidgets.QPushButton("浏览...", self.centralwidget)
        self.c_find_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.top_grid.addWidget(self.label_cookie, 1, 0)
        self.top_grid.addWidget(self.Input_cookie, 1, 1)
        self.top_grid.addWidget(self.c_find_button, 1, 2)

        # 第三行：保存路径
        self.label_save = QtWidgets.QLabel("保存至文件夹", self.centralwidget)
        self.Input_download = QtWidgets.QLineEdit(self.centralwidget)
        self.Input_download.setPlaceholderText("选择视频下载的目录...")
        self.d_find_button = QtWidgets.QPushButton("浏览...", self.centralwidget)
        self.d_find_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.top_grid.addWidget(self.label_save, 2, 0)
        self.top_grid.addWidget(self.Input_download, 2, 1)
        self.top_grid.addWidget(self.d_find_button, 2, 2)

        # 设置列宽比例，让中间的输入框自动拉伸，按钮固定宽度
        self.top_grid.setColumnStretch(1, 1)
        self.main_layout.addLayout(self.top_grid)

        # ================= 3. 中间表格区 =================
        self.mid_control_layout = QtWidgets.QHBoxLayout()
        self.label_download = QtWidgets.QLabel("可选视频格式", self.centralwidget)
        self.GetFormat = QtWidgets.QPushButton("获取解析格式", self.centralwidget)
        self.GetFormat.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.mid_control_layout.addWidget(self.label_download)
        self.mid_control_layout.addStretch() # 把按钮推到右边
        self.mid_control_layout.addWidget(self.GetFormat)
        self.main_layout.addLayout(self.mid_control_layout)

        # 表格初始化
        self.Format_list = QtWidgets.QTableWidget(self.centralwidget)
        self.Format_list.setColumnCount(7)
        self.Format_list.setHorizontalHeaderLabels(["ID", "EXT", "RESOLUTION", "FPS", "FILESIZE", "TBR", "V/A CODEC"])
        self.Format_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.Format_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.Format_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # 禁止直接编辑表格内容
        self.Format_list.setFocusPolicy(QtCore.Qt.NoFocus) # 去除选中时的虚线框
        self.Format_list.verticalHeader().setVisible(False) # 隐藏左侧默认行号

        # 设置表格列的自适应行为
        header = self.Format_list.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch) # 默认所有列自动拉伸填满
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # ID 根据内容自适应
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents) # EXT
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents) # FPS
        self.main_layout.addWidget(self.Format_list)

        # ================= 4. 底部日志区 =================
        self.bot_control_layout = QtWidgets.QHBoxLayout()
        self.label_show = QtWidgets.QLabel("运行日志", self.centralwidget)
        self.download_button = QtWidgets.QPushButton("开始下载所选内容", self.centralwidget)
        self.download_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # 给下载按钮一个醒目的颜色覆盖
        self.download_button.setStyleSheet("background-color: #a6e3a1; color: #11111b;") 
        
        self.bot_control_layout.addWidget(self.label_show)
        self.bot_control_layout.addStretch()
        self.bot_control_layout.addWidget(self.download_button)
        self.main_layout.addLayout(self.bot_control_layout)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.main_layout.addWidget(self.textBrowser)
        
        # 主布局比例设置 (让表格和日志框按 3:2 的比例分配剩余空间)
        self.main_layout.setStretchFactor(self.Format_list, 3)
        self.main_layout.setStretchFactor(self.textBrowser, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YouTube Downloader Pro"))