
import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QMovie, QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class GifCursorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Cursor Example")
        self.setGeometry(100, 100, 400, 300)

        # GIF 로드
        self.gif = QMovie("C:\\YangMJ\\xpedition_automation\\Scripts\\Python_Automation\\xpedition_layout\\net_length_calculator\\asset\\loading.gif")
        self.gif.start()  # GIF 애니메이션 시작
        self.frame_timer = QTimer(self)  # 타이머 설정
        self.frame_timer.timeout.connect(self.update_cursor)

        # 버튼 설정
        self.start_button = QPushButton("Start GIF Cursor", self)
        self.stop_button = QPushButton("Stop GIF Cursor", self)
        self.stop_button.setEnabled(False)

        # 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

        # 버튼 이벤트 연결
        self.start_button.clicked.connect(self.start_gif_cursor)
        self.stop_button.clicked.connect(self.stop_gif_cursor)

    def start_gif_cursor(self):
        """GIF 커서를 활성화"""
        self.frame_timer.start(self.gif.speed())  # GIF 속도에 맞춰 타이머 설정
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_gif_cursor(self):
        """GIF 커서를 비활성화"""
        self.frame_timer.stop()
        self.setCursor(Qt.ArrowCursor)  # 기본 커서로 복원
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_cursor(self):
        """GIF 프레임을 커서로 설정"""
        current_frame = self.gif.currentPixmap()  # 현재 GIF 프레임 가져오기
        cursor_pixmap = current_frame.scaled(32, 32, Qt.KeepAspectRatio)  # 적절히 크기 조정
        self.setCursor(QCursor(cursor_pixmap))  # 커서 업데이트


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GifCursorApp()
    window.show()
    sys.exit(app.exec_())
