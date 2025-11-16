from PyQt5.QtWidgets import QWidget, QTableWidget,QTableWidgetItem, QHeaderView, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QDateEdit, QHBoxLayout, QAbstractItemView
from PyQt5.QtCore import QDate, pyqtSignal
from PyQt5.QtGui import QFont
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stok.db')

class StokOutPage(QWidget):
    stok_updated = pyqtSignal()
    part_added = pyqtSignal()
    def __init__(self, pic):
        super().__init__()
        self.pic = pic
        self.setup_ui()
        self.load_stok_out_table()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("📤 Form Stok Keluar"))

        self.part_name_combo = QComboBox()
        self.part_name_combo.currentTextChanged.connect(self.update_part_numbers)
        layout.addWidget(QLabel("Pilih Nama Part:"))
        layout.addWidget(self.part_name_combo)

        self.part_number_combo = QComboBox()
        layout.addWidget(QLabel("Pilih Part Number:"))
        layout.addWidget(self.part_number_combo)

        # Mesin ComboBox
        self.mesin_combo = QComboBox()
        layout.addWidget(QLabel("Pilih Mesin:"))
        layout.addWidget(self.mesin_combo)

        # Kategori ComboBox
        self.kategori_combo = QComboBox()
        layout.addWidget(QLabel("Kategori:"))
        layout.addWidget(self.kategori_combo)


        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Masukkan jumlah stok keluar")
        layout.addWidget(QLabel("Jumlah (Qty):"))
        layout.addWidget(self.qty_input)

        # Lokasi ComboBox
        self.lokasi_combo = QComboBox()
        layout.addWidget(QLabel("Pilih Lokasi Penyimpanan:"))
        layout.addWidget(self.lokasi_combo)

        self.tanggal_input = QDateEdit()
        self.tanggal_input.setDate(QDate.currentDate())
        self.tanggal_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Tanggal Keluar:"))
        layout.addWidget(self.tanggal_input)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Simpan Stok Keluar")
        self.save_btn.clicked.connect(self.simpan_stok_out)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_part_names()

        # Tabel Stok Out
        table_box = QVBoxLayout()
        self.stok_out_table = QTableWidget()
        self.stok_out_table.setColumnCount(8)
        self.stok_out_table.setHorizontalHeaderLabels(["Part Name", "Part Number", "Mesin", "Kategori", "Lokasi", "Tanggal", "Qty Out", "PIC"])
        self.stok_out_table.setSortingEnabled(True)
        self.stok_out_table.verticalHeader().setVisible(False)
        self.stok_out_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stok_out_table.setStyleSheet("""
            QTableWidget {
                background-color: #f0f0f0;
                alternate-background-color: #e0e0e0;
                selection-background-color: #337ab7;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #337ab7;
                color: white;
                padding: 5px;
            }
        """)
        font = QFont("Segoe UI", 10)
        self.stok_out_table.setFont(font)
        self.stok_out_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stok_out_table.setSortingEnabled(True)
        table_box.addWidget(self.stok_out_table)
        layout.addWidget(QLabel("Tabel Stok Out:"))
        layout.addLayout(table_box)

    def load_part_names(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Ambil hanya part yang punya stok masuk
            cursor.execute("""
                SELECT DISTINCT "part name"
                FROM balance
                WHERE qty_blc > 0
            """)
            names = cursor.fetchall()
            conn.close()

            self.part_name_combo.clear()
            for name in names:
                self.part_name_combo.addItem(name[0])
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat nama part: {e}")

    def update_part_numbers(self, part_name):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT DISTINCT "part number" 
                FROM balance 
                WHERE "part name" = ? AND qty_blc > 0 
            """, (part_name,))
            numbers = cursor.fetchall()
            conn.close()
            self.part_number_combo.clear()
            for num in numbers:
                self.part_number_combo.addItem(num[0])
            self.part_number_combo.currentTextChanged.connect(self.update_part_info)
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat part number: {e}")

    def update_part_info(self, part_number):
        try:
            part_name = self.part_name_combo.currentText()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT mesin, kategori, lokasi FROM balance WHERE "part number" = ? AND "part name" = ?',
                (part_number, part_name)
            )
            results = cursor.fetchall()
            conn.close()
            self.kategori_combo.clear()
            self.mesin_combo.clear()
            self.lokasi_combo.clear()
            kategori_list = []
            mesin_list = []
            lokasi_list = []
            for row in results:
                mesin_list.append(row[0])
                kategori_list.append(row[1])
                lokasi_list.append(row[2])
            self.mesin_combo.addItems(list(set(mesin_list)))
            self.kategori_combo.addItems(list(set(kategori_list)))
            self.lokasi_combo.addItems(list(set(lokasi_list)))
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat info part: {e}")

    def load_stok_out_table(self):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT "part name", "part number", mesin, kategori, lokasi, tanggal, qty_out, pic
                    FROM stok_out
                """)
                rows = cursor.fetchall()
                conn.close()
                self.stok_out_table.setRowCount(len(rows))
                for row_index, row in enumerate(rows):
                    for column_index, value in enumerate(row):
                        self.stok_out_table.setItem(row_index, column_index, QTableWidgetItem(str(value)))
            except Exception as e:
                QMessageBox.critical(self, "Gagal", f"Gagal memuat tabel stok_out: {e}")

    def simpan_stok_out(self):
        part_name = self.part_name_combo.currentText()
        part_number = self.part_number_combo.currentText()
        mesin = self.mesin_combo.currentText()
        kategori = self.kategori_combo.currentText()
        lokasi = self.lokasi_combo.currentText()
        qty_text = self.qty_input.text()
        tanggal = self.tanggal_input.date().toString("yyyy-MM-dd")
        if not qty_text or not part_name or not part_number or not mesin or not kategori or not lokasi:
            QMessageBox.warning(self, "Input Salah", "Semua kolom wajib diisi!")
            return
        try:
            qty_out = int(qty_text)
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Qty harus berupa angka!")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Cek stok tersedia
            cursor.execute(""" 
                SELECT qty_blc 
                FROM balance 
                WHERE "part name" = ? and "part number" = ? AND mesin = ? AND kategori = ? AND lokasi = ?
            """, (part_name, part_number, mesin, kategori, lokasi))
            available = cursor.fetchone()
            if available:
                available = available[0]
            else:
                available = 0
            if qty_out > available:
                QMessageBox.warning(self, "Gagal", "Stok tidak cukup!")
                conn.close()
                return
            # Simpan stok keluar
            cursor.execute(""" 
                INSERT INTO stok_out ("part name", "part number", mesin, kategori, lokasi, tanggal, qty_out, pic) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
            """, (part_name, part_number, mesin, kategori, lokasi, tanggal, qty_out, self.pic))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sukses", f"Stok keluar oleh '{self.pic}' berhasil disimpan.")
            self.qty_input.clear()
            self.tanggal_input.setDate(QDate.currentDate())
            self.stok_updated.emit()
            self.load_part_names()
            self.load_stok_out_table()
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menyimpan data: {e}")
