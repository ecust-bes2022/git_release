import sys
import time
import threading
from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QProgressBar, QToolBar, QAction
from client_config import get_updater

def do_work(progress_signal):
    for i in range(101):
        time.sleep(0.1)
        progress_signal.emit(i) # 发送进度信号

class MainWindow(QMainWindow):
    progress_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.resize(300, 200)

        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 添加用于更新的工具栏动作
        update_action = QAction('Update', self)
        update_action.triggered.connect(self.update_app)
        toolbar.addAction(update_action)

        # 添加用于启动工作线程的按钮
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setGeometry(100, 50, 100, 30)
        self.start_btn.clicked.connect(self.start_worker)

    def start_worker(self):
        self.worker_thread = threading.Thread(target=do_work, args=(self.progress_signal,))
        self.worker_thread.start()

        self.progress_dialog = ProgressDialog(self, self.progress_signal)
        self.progress_dialog.show()

    def update_app(self):
        updater = get_updater()
        app_update = updater.update_check(updater.app_name, updater.app_version, channel='stable')

        if app_update is not None:
            print('Update available')
            app_update.download()

            if app_update.is_downloaded():
                app_update.extract_restart()

        else:
            print('No updates found')

class ProgressDialog(QDialog):
    def __init__(self, parent=None, progress_signal=None):
        super().__init__(parent)
        self.setWindowTitle('Progress Dialog')
        self.resize(300, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 30, 200, 30)

        if progress_signal:
            progress_signal.connect(self.show_progress) # 接收进度信号

    def show_progress(self, value):
        self.progress_bar.setValue(value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

