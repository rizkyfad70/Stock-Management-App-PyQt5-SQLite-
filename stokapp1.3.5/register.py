from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsBlurEffect, QSpacerItem, QSizePolicy
from models.user_model import user_exists, register_user
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt

class RegisterForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Register')
        self.setFixedSize(900, 600)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setup_ui()

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
        blur.setBlurRadius(1)
        bg_label.setGraphicsEffect(blur)

        # Overlay gradasi
        overlay = QLabel(self)
        overlay.setGeometry(0, 0, 900, 600)
        overlay.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,0,0,100),
                stop:1 rgba(0,0,0,180)
            );
        """)

        # Layout utama
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Spacer atas
        outer_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

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

        # Posisikan di kanan atas jendela
        top_widget.move(self.width() - top_widget.width() - 10, 10)
        top_widget.raise_()  # pastikan selalu di atas layer lain

        # Container transparan untuk form
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0,0,0,0.6);
                border-radius: 15px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)
        form_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Judul
        title = QLabel("Sign Up")
        title.setFont(QFont("Poppins", 28, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        form_layout.addWidget(title)

        # Input Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedSize(280, 40)
        self.username_input.setStyleSheet(self.input_style())
        form_layout.addWidget(self.username_input, alignment=QtCore.Qt.AlignCenter)

        # Input Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(280, 40)
        self.password_input.setStyleSheet(self.input_style())
        form_layout.addWidget(self.password_input, alignment=QtCore.Qt.AlignCenter)

        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFixedSize(280, 40)
        self.confirm_password_input.setStyleSheet(self.input_style())
        self.confirm_password_input.returnPressed.connect(self.register)
        form_layout.addWidget(self.confirm_password_input, alignment=QtCore.Qt.AlignCenter)

        # Register button
        register_btn = QPushButton("Register")
        register_btn.setFixedSize(280, 40)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #0072ff, stop:1 #00c6ff);
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
        register_btn.clicked.connect(self.register)
        register_btn.setDefault(True)
        form_layout.addWidget(register_btn, alignment=QtCore.Qt.AlignCenter)

        # Tambahkan form ke outer layout
        outer_layout.addWidget(form_container, alignment=QtCore.Qt.AlignCenter)

        # Spacer bawah
        outer_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

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


    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Gagal", "Semua kolom wajib diisi.")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Gagal", "Password minimal 8 karakter.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Gagal", "Password dan konfirmasi password tidak cocok.")
            return

        if user_exists(username):
            QMessageBox.warning(self, "Gagal", "Username sudah terpakai.")
        else:
            register_user(username, password)
            QMessageBox.information(self, "Sukses", "Akun berhasil dibuat.")
            from login import LoginForm  
            self.login_window = LoginForm()
            self.login_window.show()
            self.close()