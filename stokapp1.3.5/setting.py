from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import pyqtSignal
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stok.db')

class TambahPartPage(QWidget):
    part_added = pyqtSignal()  # sinyal untuk memberitahu halaman lain agar refresh

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_part_list()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("➕ Tambah Part Baru")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Part Name:"))
        self.part_name_input = QLineEdit()
        layout.addWidget(self.part_name_input)

        layout.addWidget(QLabel("Part Number:"))
        self.part_number_input = QLineEdit()
        layout.addWidget(self.part_number_input)

        layout.addWidget(QLabel("Mesin:"))
        self.mesin_combo = QComboBox()
        self.load_mesin()
        layout.addWidget(self.mesin_combo)

        layout.addWidget(QLabel("Kategori:"))
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(["New", "Second"])
        layout.addWidget(self.kategori_combo)

        self.submit_btn = QPushButton("💾 Simpan Part")
        self.submit_btn.clicked.connect(self.simpan_part)
        layout.addWidget(self.submit_btn)

        layout.addWidget(QLabel("📋 Daftar Part Terdaftar:"))
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Part Name", "Part Number", "Mesin", "Kategori"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        layout.addStretch()
        self.setLayout(layout)

    def load_mesin(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT mesin FROM mesin")
            mesin_list = cursor.fetchall()
            conn.close()

            self.mesin_combo.clear()
            for item in mesin_list:
                self.mesin_combo.addItem(item[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data mesin: {e}")

    def load_part_list(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT `part name`, `part number`, mesin, kategori FROM data_part ORDER BY `part name` ASC")
            data = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar part: {e}")

    def simpan_part(self):
        part_name = self.part_name_input.text().strip()
        part_number = self.part_number_input.text().strip()
        mesin = self.mesin_combo.currentText()
        kategori = self.kategori_combo.currentText()

        if not part_name or not part_number:
            QMessageBox.warning(self, "Input Error", "Part Name dan Part Number wajib diisi.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO data_part ("part name", "part number", mesin, kategori)
                VALUES (?, ?, ?, ?)
            """, (part_name, part_number, mesin, kategori))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sukses", "Part berhasil ditambahkan!")
            self.part_name_input.clear()
            self.part_number_input.clear()
            self.mesin_combo.setCurrentIndex(0)
            self.kategori_combo.setCurrentIndex(0)

            # refresh tabel daftar part dan kirim sinyal supaya halaman lain update
            self.load_part_list()
            self.part_added.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{str(e)}")
