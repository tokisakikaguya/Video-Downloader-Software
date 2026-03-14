import os
import sys
import yt_dlp
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import Ui_yt_download  # 导入UI界面类
import warnings
import traceback
import re
from PyQt5.QtWidgets import QMessageBox, QApplication

class StdErrRedirector:
    """将stderr重定向到textBrowser中"""
    def __init__(self, text_browser):
        self.text_browser = text_browser

    def write(self, message):
        """捕获写入stderr的消息,并将其显示到textBrowser"""
        if message != '\n':  # 避免打印空行
            self.text_browser.append(message)

    def flush(self):
        """必须实现flush方法"""
        pass

class WarningRedirector:
    """将警告重定向到textBrowser中"""
    def __init__(self, text_browser):
        self.text_browser = text_browser

    def __call__(self, message, category, filename, lineno, file=None, line=None):
        """捕获警告信息，并将其显示到textBrowser"""
        warning_message = f"Warning: {str(message)}"
        self.text_browser.append(warning_message)

# ================= 新增：独立的工作线程类 =================
class DownloadWorker(QThread):
    # 定义信号，用于与主线程进行跨线程通信
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, video_url, ydl_opts, parent=None):
        super().__init__(parent)
        self.video_url = video_url
        self.ydl_opts = ydl_opts
        # 用于移除ANSI转义序列的正则表达式
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # 使用 yt-dlp 提供的结构化字段，比解析字符串更稳定
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            if percent:
                msg = f"[下载进度]: {percent} | 速度: {speed} | 剩余时间: {eta}"
                msg = self.ansi_escape.sub('', msg)
                self.progress_signal.emit(msg)  # 发送进度信号
                
        elif d['status'] == 'finished':
            self.finished_signal.emit(f"\n[下载完成]: {d.get('filename')}")
            
        elif d['status'] == 'error':
            self.error_signal.emit(f"\n[下载出错]: {d.get('filename')} - {d.get('error', 'Unknown error')}")

    def run(self):
        """线程启动时执行的函数"""
        try:
            # 设置yt-dlp的钩子函数到当前实例的方法
            self.ydl_opts['progress_hooks'] = [self.progress_hook]
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.video_url])
        except Exception as e:
            error_message = traceback.format_exc()
            self.error_signal.emit(f"后台下载发生异常:\n{error_message}")
# ==========================================================

class Window(Ui_yt_download.Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        # 按键设置
        self.c_find_button.clicked.connect(self.cookie_path)
        self.d_find_button.clicked.connect(self.choose_save)
        self.GetFormat.clicked.connect(self.get_video_options)
        self.download_button.clicked.connect(self.download_video)

        # 重定向stderr到textBrowser
        self.stderr_redirector = StdErrRedirector(self.textBrowser)
        sys.stderr = self.stderr_redirector  # 重定向标准错误输出
        # 重定向警告到textBrowser
        self.warning_redirector = WarningRedirector(self.textBrowser)
        warnings.showwarning = self.warning_redirector  # 重定向警告输出

    # 设置具体功能
    def show_warning(self, message, category, filename, lineno, file=None, line=None):
        warning_message = f"Warning: {str(message)} (In {filename}, Line {lineno})"
        print(warning_message)  # 输出到终端
        self.textBrowser.append(warning_message)  # 输出到textBrowser

    def cookie_path(self):
        cookies, _ = QtWidgets.QFileDialog.getOpenFileName(None,"选取cookies文件",os.getcwd(),"All Files(*);;Text Files(*.txt)")
        self.Input_cookie.setText(cookies)

    def choose_save(self):
        saves = QtWidgets.QFileDialog.getExistingDirectory(None,"选取保存路径",os.getcwd())
        self.Input_download.setText(saves)

    def get_video_options(self):
        """调用 yt-dlp 获取视频选项"""
        self.video_url = self.Input_url.text().strip()
        self.cookie_path = self.Input_cookie.text().strip()  # 获取cookie路径

        self.Format_list.clear()

        if not self.video_url:
            self.textBrowser.append("Please provide a valid URL.")
            return
        
        if not self.cookie_path:
            self.textBrowser.append("Please select a cookie file.")
            return

        # 设置yt-dlp的下载选项
        self.ydl_opts = {
            'quiet': True,  # 禁用输出，只显示必要的信息
            'extract_flat': True,  # 提取并列出所有格式的链接
            'cookiefile': self.cookie_path,  # 使用cookie文件
        }

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                formats = info.get('formats', [])
                if not formats:
                    print("No formats found!")
                    return
                
                self.Format_list.clear()  
                self.Format_list.setRowCount(0)  
                self.Format_list.setHorizontalHeaderLabels(["ID", "EXT", "RESOLUTION", "FPS", "FILESIZE", "TBR", "V/A CODEC"]) 

                for fmt in formats:
                    format_id = fmt.get('format_id', 'N/A')
                    if not format_id.isdigit():  
                        continue
                    ext = fmt.get('ext', 'N/A')
                    resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}" if fmt.get('width') and fmt.get('height') else 'audio only'
                    fps = fmt.get('fps') if fmt.get('fps') is not None else 'N/A'
                    filesize = f"{fmt.get('filesize', 0) / 1024 / 1024:.2f} MiB" if fmt.get('filesize') else 'N/A'
                    tbr = fmt.get('tbr', 'N/A')
                    vcodec = fmt.get('vcodec', 'N/A')
                    acodec = fmt.get('acodec', 'N/A')
                    codec = f"{vcodec} / {acodec}"

                    row_position = self.Format_list.rowCount()
                    self.Format_list.insertRow(row_position)

                    format_id_item = QtWidgets.QTableWidgetItem(format_id)
                    format_id_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 0, format_id_item)

                    ext_item = QtWidgets.QTableWidgetItem(ext)
                    ext_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 1, ext_item)

                    resolution_item = QtWidgets.QTableWidgetItem(resolution)
                    resolution_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 2, resolution_item)

                    fps_item = QtWidgets.QTableWidgetItem(str(fps))
                    fps_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 3, fps_item)

                    filesize_item = QtWidgets.QTableWidgetItem(filesize)
                    filesize_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 4, filesize_item)

                    tbr_item = QtWidgets.QTableWidgetItem(str(tbr))
                    tbr_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 5, tbr_item)

                    codec_item = QtWidgets.QTableWidgetItem(codec)
                    codec_item.setTextAlignment(Qt.AlignCenter)
                    self.Format_list.setItem(row_position, 6, codec_item)

        except yt_dlp.utils.ExtractorError as e:
            error_message = str(e)  
            self.textBrowser.append(f"yt-dlp Error: {error_message}")
    
    def on_row_selected(self):
        """当选中某一行时，获取该行的 format_id"""
        selected_row = self.Format_list.currentRow()
        if selected_row == -1:  
            return
        
        format_id_item = self.Format_list.item(selected_row, 0)
        if format_id_item:
            format_id = format_id_item.text()
            print(f"Selected format_id: {format_id}")
            self.textBrowser.append(f"Selected format_id: {format_id}")
    
    def download_video(self):
        try:
            selected_indexes = self.Format_list.selectedIndexes()
            if not selected_indexes:
                self.textBrowser.append("请选择要下载的文件。")
                return
            
            selected_format_ids = []
            seen_rows = set()

            for index in selected_indexes:
                row = index.row()
                if row not in seen_rows:
                    seen_rows.add(row)
                    format_id_item = self.Format_list.item(row, 0)
                    if format_id_item:
                        format_id = format_id_item.text()
                        selected_format_ids.append(format_id)

            if selected_format_ids:
                reply = QMessageBox.question(MainWindow, '确认下载', 
                                            f"您选择的format_id是: {'+ '.join(selected_format_ids)}\n\n"
                                            "是否开始下载？", 
                                            QMessageBox.Yes | QMessageBox.No, 
                                            QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.textBrowser.append(f"开始下载格式ID: {', '.join(selected_format_ids)}")
                    self.download_selected_format_ids(selected_format_ids)
                else:
                    self.textBrowser.append("下载操作已取消。")
            else:
                self.textBrowser.append("没有选中任何格式ID。")
        except Exception as e:
            error_message = traceback.format_exc()
            self.textBrowser.append(f"发生错误:\n{error_message}")
            print(error_message)
    
    def download_selected_format_ids(self, format_ids):
        self.download_dir = self.Input_download.text().strip()
        if not self.download_dir:
            self.textBrowser.append("Please provide a download dir.")
            return
        
        if len(format_ids) > 1:
            selected_format_id = '+'.join(format_ids)
        else:
            selected_format_id = format_ids[0]

        try:
            self.ydl_opts.update({
                'format': selected_format_id,
                'outtmpl': os.path.join(self.download_dir, '%(title)s%(id)s.%(ext)s'),
                'cookiefile': self.cookie_path,
            })
            
            self.textBrowser.append(f"\n初始化下载引擎，目标格式ID: {selected_format_id}")
            
            # 禁用下载按钮，防止用户在下载过程中重复点击引发多线程冲突
            self.download_button.setEnabled(False)

            # 实例化并启动后台下载线程
            self.worker = DownloadWorker(self.video_url, self.ydl_opts)
            
            # 绑定信号到主线程的槽函数
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.finished_signal.connect(self.textBrowser.append)
            self.worker.error_signal.connect(self.textBrowser.append)
            
            # 下载结束后恢复下载按钮
            self.worker.finished.connect(lambda: self.download_button.setEnabled(True))
            
            self.worker.start()  # 启动线程！

        except Exception as e:
            error_message = traceback.format_exc()
            self.textBrowser.append(f"下载初始化过程发生错误:\n{error_message}")

    def update_progress(self, msg):
        """
        动态更新 TextBrowser 中的进度条。
        通过识别是否是进度信息，来覆盖最后一行，防止被成千上万行进度日志刷屏卡顿。
        """
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        
        # 如果当前最后一行是下载进度，就先删除它，再添加新的进度
        if cursor.selectedText().startswith("[下载进度]:"):
            cursor.removeSelectedText()
            cursor.deletePreviousChar() # 删除多余的换行符
            
        self.textBrowser.append(msg)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Window(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())