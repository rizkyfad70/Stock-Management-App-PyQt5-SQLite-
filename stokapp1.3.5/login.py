from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGraphicsBlurEffect, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtCore
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from models.user_model import check_user
from register import RegisterForm
from main_dashboard import MainWindow

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setFixedSize(900, 600)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setup_ui()
        self.add_animation()

    def setup_ui(self):
        # Background image
        bg_label = QLabel(self)
        pixmap = QPixmap("assets/background.jpg").scaled(
            900, 600,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        bg_label.setPixmap(pixmap)
        bg_label.setGeometry(0, 0, 900, 600)

        # Blur effect
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(2)
        bg_label.setGraphicsEffect(blur)

        # Overlay gradasi
        overlay = QLabel(self)
        overlay.setGeometry(0, 0, 900, 600)
        overlay.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,0,0,120),
                stop:1 rgba(0,0,0,200)
            );
        """)

        # Outer layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Spacer atas
        outer_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # === Tombol minimize & exit ===
        top_widget = QWidget(self)
        top_widget.setFixedSize(50, 24)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        # Tombol minimize
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(22, 22)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #008ecc;
            }
        """)
        self.min_btn.clicked.connect(self.showMinimized)
        top_layout.addWidget(self.min_btn)

        # Tombol exit
        self.exit_btn = QPushButton("✕")
        self.exit_btn.setFixedSize(22, 22)
        self.exit_btn.setStyleSheet(""" 
            QPushButton { 
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: white;
                font-size: 14px;
            } 
            QPushButton:hover { 
                background-color: #ff4d6d;
            } 
        """)
        self.exit_btn.clicked.connect(self.close)
        top_layout.addWidget(self.exit_btn)

        # Posisikan tombol
        top_widget.move(self.width() - top_widget.width() - 10, 10)
        top_widget.raise_()

        # Card transparan untuk login
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0,0,0,0.4);
                border-radius: 15px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)
        form_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Logo
        #logo = QLabel()
        #logo.setPixmap(QPixmap("assets/logo.png").scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        #logo.setAlignment(QtCore.Qt.AlignCenter)
        #form_layout.addWidget(logo)

        # Title
        title = QLabel("Sign In")
        title.setFont(QFont("Poppins", 28, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        form_layout.addWidget(title)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedSize(280, 40)
        self.username_input.setStyleSheet(self.input_style())
        form_layout.addWidget(self.username_input, alignment=QtCore.Qt.AlignCenter)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(280, 40)
        self.password_input.setStyleSheet(self.input_style())
        form_layout.addWidget(self.password_input, alignment=QtCore.Qt.AlignCenter)

        # Enter untuk login
        self.password_input.returnPressed.connect(self.login)

        # Login button
        self.login_btn = QPushButton("🔑 Login")
        self.login_btn.setFixedSize(280, 40)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #0072ff, stop:1 #0072ff);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 15px;
                font-family: Poppins;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #00c6ff, stop:1 #0072ff);
            }
        """)
        self.login_btn.setText("Loading...")
        QtCore.QTimer.singleShot(1500, lambda: self.login_btn.setText("Login"))

        self.login_btn.clicked.connect(self.login)
        self.login_btn.setDefault(True)
        form_layout.addWidget(self.login_btn, alignment=QtCore.Qt.AlignCenter)

        # Register link
        self.register_btn = QPushButton("Create new account")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #aaa;
                font-size: 13px;
                font-family: Poppins;
            }
            QPushButton:hover {
                color: white;
                text-decoration: underline;
            }
        """)
        self.register_btn.clicked.connect(self.open_register)
        form_layout.addWidget(self.register_btn, alignment=QtCore.Qt.AlignCenter)

        # Footer versi aplikasi
        footer = QLabel("Stock Maintenance System v1.0 ©2025")
        footer.setStyleSheet("color: #888; font-size: 11px;")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        form_layout.addWidget(footer)

        outer_layout.addWidget(form_container, alignment=QtCore.Qt.AlignCenter)

        # Spacer bawah
        outer_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def add_animation(self):
        """Efek fade-in saat window muncul"""
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    def input_style(self):
        return """
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
                background-color: rgba(255,255,255,0.05);
                color: white;
                font-family: Poppins;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00aaff;
                background-color: rgba(255,255,255,0.1);
            }
        """

    def input_style(self):
        return """
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
                background-color: rgba(255,255,255,0.05);
                color: white;
                font-family: Poppins;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00aaff;
                background-color: rgba(255,255,255,0.1);
            }
        """

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if check_user(username, password):
            QMessageBox.information(self, "Selamat Datang", f"Halo {username}, selamat bekerja!")
            self.close()
            self.dashboard = MainWindow(username)
            self.dashboard.setWindowOpacity(0)
            self.dashboard.show()
            
             # Animasi fade-in
            self.anim = QPropertyAnimation(self.dashboard, b"windowOpacity")
            self.anim.setDuration(800)  # durasi 0.8 detik
            self.anim.setStartValue(0)
            self.anim.setEndValue(1)
            self.anim.setEasingCurve(QEasingCurve.InOutQuad)
            self.anim.start()

        else:
            QMessageBox.warning(self, "Gagal", "Username atau password salah.")

    def open_register(self):
        self.close()
        self.register_window = RegisterForm()
        self.register_window.setWindowOpacity(0)  # mulai transparan
        self.register_window.show()

        # Animasi fade-in
        self.anim = QPropertyAnimation(self.register_window, b"windowOpacity")
        self.anim.setDuration(800)  # durasi 0.8 detik
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

        
