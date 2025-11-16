from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore
import sys

from dashboard import Dashboard
from tambah_part import TambahPartPage
from stok_in import StokInPage
from stok_out import StokOutPage

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Stock Maintenance System")
        #self.showFullScreen()
        self.showNormal()
        #self.setFixedSize(1000, 600)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.setWindowFlags(Qt.Window)
        
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(main_widget)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(15)

        # Header 
        title = QLabel("📦 Stock System")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)


        sidebar_layout.addSpacing(30)  # jarak ke tombol

        btn_dashboard = QPushButton("Dashboard")
        btn_tambah = QPushButton("Tambah Part")
        btn_in = QPushButton("Stock In")
        btn_out = QPushButton("Stock Out")

        for btn in (btn_dashboard, btn_tambah, btn_in, btn_out):
            btn.setFixedHeight(40)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    border: none;
                    #font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # user label
        user_label = QLabel(f"👤 {username}")
        user_label.setFont(QFont("Segoe UI", 10))
        #ser_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(user_label)

        # Tombol keluar
        btn_exit = QPushButton("Logout")
        btn_exit.setFixedHeight(35)
        btn_exit.setFont(QFont("Segoe UI", 10))
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sidebar_layout.addWidget(btn_exit)

        # Content area (stack)
        self.stack = QStackedWidget()
        self.page_dashboard = Dashboard(username)
        self.page_tambah = TambahPartPage()
        self.page_in = StokInPage(pic=username)
        self.page_out = StokOutPage(pic=username)

        # add pages
        self.stack.addWidget(self.page_dashboard)  # index 0
        self.stack.addWidget(self.page_tambah)     # index 1
        self.stack.addWidget(self.page_in)         # index 2
        self.stack.addWidget(self.page_out)        # index 3

        # connect sidebar
        btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_tambah.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_in.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_out.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_exit.clicked.connect(self.close)

        # Integrasi sinyal untuk sinkronisasi data:
        # - Kalau tambah part -> stok_in harus reload nama part & dashboard reload stok
        #self.page_tambah.part_added.connect(self.page_in.load_part_names)
        #self.page_tambah.part_added.connect(self.page_dashboard.load_stok_tersedia)

        

        # Integrasi sinyal untuk sinkronisasi data:
        self.page_tambah.part_added.connect(self.page_in.load_part_names)
        self.page_tambah.part_added.connect(self.page_out.load_part_names)
        self.page_tambah.part_added.connect(self.page_dashboard.refresh_summary)
        self.page_tambah.lokasi_added.connect(self.page_in.load_lokasi)
        #self.page_tambah.mesin_added.connect(self.page_in.load_)
        self.page_in.part_added.connect(self.page_out.load_part_names)
        
        # - Kalau stok masuk/out -> dashboard reload stok
        self.page_in.stok_updated.connect(self.page_dashboard.refresh_summary)
        self.page_out.stok_updated.connect(self.page_dashboard.refresh_summary)
        self.page_out.stok_updated.connect(self.page_in.load_stok_act)
        self.page_out.stok_updated.connect(self.page_in.load_stok_out_table)
        
        self.page_tambah.part_added.connect(self.page_dashboard.load_table)
        self.page_in.stok_updated.connect(self.page_dashboard.load_table)
        self.page_out.stok_updated.connect(self.page_dashboard.load_table)

        # add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load FHJ
#with open("table.qss", "r") as f:
#    qss = f.read()
#    app.setStyleSheet(qss)
    window = MainWindow("Admin")
    window.show()
    sys.exit(app.exec_())
