from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
    QInputDialog, QFrame, QTabWidget, QFormLayout, QFileDialog, QDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stok.db')

class TambahPartPage(QWidget):
    part_added = pyqtSignal()
    lokasi_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(self._global_style())
        self.setup_ui()
        self.load_mesin()
        self.load_lokasi()
        self.load_part_list()
        self.load_mesin_list()
        self.load_lokasi_list()

    def _global_style(self):
        return """
        QWidget { font-family: 'Segoe UI'; font-size: 12px; color: #1f2937; }
        QLabel { font-weight: 500; color: #111827; }
        QPushButton { 
            background-color: #3b82f6; color: white; 
            border-radius: 6px; padding: 6px 12px; font-weight: bold;
        }
        QPushButton:hover { background-color: #2563eb; }
        QLineEdit, QComboBox { 
            border: 1px solid #d1d5db; border-radius: 6px; padding: 6px; 
        }
        QTableWidget { 
            border: 1px solid #d1d5db; border-radius: 6px; gridline-color: #e5e7eb;
        }
        QHeaderView::section { 
            background-color: #f3f4f6; font-weight: bold; 
        }
        """

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setSpacing(15)
        root_layout.setContentsMargins(15, 15, 15, 15)

        # ---------------- Header ----------------
        header = QLabel("➕ Tambah Part Baru")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white; 
            background-color: #3b82f6; padding: 10px; border-radius: 6px;
        """)
        root_layout.addWidget(header)

        # ---------------- Main Layout ----------------
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        root_layout.addLayout(main_layout)

        # ---------------- Form Input (dalam card) ----------------
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Input fields
        self.part_name_input = QLineEdit()
        self.part_number_input = QLineEdit()

        self.mesin_combo = QComboBox()
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(["New", "Second"])
        self.lokasi_combo = QComboBox()

        # Tambah gambar
        self.gambar_path = None
        self.gambar_btn = QPushButton("🖼️ Pilih Gambar")
        self.gambar_btn.clicked.connect(self.pilih_gambar)

        # Tambahkan ke form
        form_layout.addRow("Part Name:", self.part_name_input)
        form_layout.addRow("Part Number:", self.part_number_input)
        form_layout.addRow("Mesin:", self.mesin_combo)
        form_layout.addRow("Kategori:", self.kategori_combo)
        form_layout.addRow("Lokasi:", self.lokasi_combo)
        form_layout.addWidget(self.gambar_btn)

        # Tombol simpan
        self.submit_btn = QPushButton("💾 Simpan Part")
        self.submit_btn.setFixedHeight(32)
        self.submit_btn.clicked.connect(self.simpan_part)
        form_layout.addRow("", self.submit_btn)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame, 1)

        # ---------------- Tab untuk tabel ----------------
        self.tabs = QTabWidget()

        # Tab Part
        part_tab = QWidget()
        part_layout = QVBoxLayout(part_tab)

        # search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari part...")
        self.search_input.textChanged.connect(self.filter_part_list)
        part_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Part Name", "Part Number", "Mesin", "Kategori"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        part_layout.addWidget(self.table)
        self.table.cellClicked.connect(self.show_gambar)
        #self.gambar_label = QLabel("Klik part number untuk preview")
        #self.gambar_label.setAlignment(Qt.AlignCenter)
        #part_layout.addWidget(self.gambar_label)
        self.tabs.addTab(part_tab, "📋 Daftar Part")

        # Tab Mesin
        mesin_tab = QWidget()
        mesin_layout = QVBoxLayout(mesin_tab)
        self.mesin_table = QTableWidget()
        self.mesin_table.setColumnCount(1)
        self.mesin_table.setHorizontalHeaderLabels(["Mesin"])
        self.mesin_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        mesin_layout.addWidget(self.mesin_table)

        self.add_mesin_btn = QPushButton("➕ Tambah Mesin")
        self.add_mesin_btn.clicked.connect(self.tambah_mesin_dialog)
        mesin_layout.addWidget(self.add_mesin_btn)

        self.tabs.addTab(mesin_tab, "🛠️ Mesin")

        # Tab Lokasi
        lokasi_tab = QWidget()
        lokasi_layout = QVBoxLayout(lokasi_tab)
        self.lokasi_table = QTableWidget()
        self.lokasi_table.setColumnCount(1)
        self.lokasi_table.setHorizontalHeaderLabels(["Lokasi"])
        self.lokasi_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lokasi_layout.addWidget(self.lokasi_table)

        self.add_lokasi_btn = QPushButton("➕ Tambah Lokasi")
        self.add_lokasi_btn.clicked.connect(self.tambah_lokasi_dialog)
        lokasi_layout.addWidget(self.add_lokasi_btn)

        self.tabs.addTab(lokasi_tab, "📍 Lokasi")

        main_layout.addWidget(self.tabs, 2)

        self.setLayout(root_layout)

    # ---------------- Load Data ----------------
    def load_mesin(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT mesin FROM mesin ORDER BY mesin ASC")
            mesin_list = cursor.fetchall()
            conn.close()
            self.mesin_combo.clear()
            for item in mesin_list:
                self.mesin_combo.addItem(item[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data mesin: {e}")

    def load_lokasi(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT lokasi FROM lokasi ORDER BY lokasi ASC")
            lokasi_list = cursor.fetchall()
            conn.close()
            self.lokasi_combo.clear()
            for item in lokasi_list:
                self.lokasi_combo.addItem(item[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data lokasi: {e}")

    def load_part_list(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT `part name`, `part number`, mesin, kategori
                FROM data_part 
                ORDER BY `part name` ASC
            """)
            data = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar part: {e}")

    def load_mesin_list(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT mesin FROM mesin ORDER BY mesin ASC")
            data = cursor.fetchall()
            conn.close()

            self.mesin_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                self.mesin_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar mesin: {e}")

    def load_lokasi_list(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT lokasi FROM lokasi ORDER BY lokasi ASC")
            data = cursor.fetchall()
            conn.close()

            self.lokasi_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                self.lokasi_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat daftar lokasi: {e}")

    # ---------------- Filter Tabel Part ----------------
    def filter_part_list(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    # ---------------- Simpan Part ----------------
    def simpan_part(self):
        part_name = self.part_name_input.text().strip()
        part_number = self.part_number_input.text().strip()
        mesin = self.mesin_combo.currentText()
        kategori = self.kategori_combo.currentText()
        lokasi = self.lokasi_combo.currentText()  # hanya dipilih, tidak disimpan

        if not part_name or not part_number:
            QMessageBox.warning(self, "Input Error", "Part Name dan Part Number wajib diisi.")
            return

        gambar_data = getattr(self, "gambar_data", None)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO data_part ("part name", "part number", mesin, kategori, gambar)
                VALUES (?, ?, ?, ?, ?)
            """, (part_name, part_number, mesin, kategori, gambar_data))
            conn.commit()
            conn.close()

            self.load_part_list()
            self.part_added.emit()
            QMessageBox.information(self, "Sukses", "Part berhasil ditambahkan!")
            self.part_name_input.clear()
            self.part_number_input.clear()
            self.mesin_combo.setCurrentIndex(0)
            self.kategori_combo.setCurrentIndex(0)
            self.lokasi_combo.setCurrentIndex(0)
            self.gambar_btn.setText("🖼️ Pilih Gambar")
            self.gambar_path = None
            self.gambar_data = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{str(e)}")

    # ---------------- Tambah Mesin ----------------
    def tambah_mesin_dialog(self):
        text, ok = QInputDialog.getText(self, "Tambah Mesin", "Nama Mesin:")
        if ok and text.strip():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO mesin (mesin) VALUES (?)", (text.strip(),))
                conn.commit()
                conn.close()
                self.load_mesin()
                self.load_mesin_list()
                QMessageBox.information(self, "Sukses", f"Mesin '{text}' berhasil ditambahkan!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan mesin: {e}")

    # ---------------- Tambah Lokasi ----------------
    def tambah_lokasi_dialog(self):
        text, ok = QInputDialog.getText(self, "Tambah Lokasi", "Nama Lokasi:")
        if ok and text.strip():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO lokasi (lokasi) VALUES (?)", (text.strip(),))
                conn.commit()
                conn.close()
                self.load_lokasi()
                self.load_lokasi_list()
                self.lokasi_added.emit()
                QMessageBox.information(self, "Sukses", f"Lokasi '{text}' berhasil ditambahkan!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan lokasi: {e}")

    def pilih_gambar(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.gambar_path = file_name  # simpan path supaya bisa direset di UI
            with open(file_name, "rb") as f:
                self.gambar_data = f.read()  # simpan binary untuk disimpan ke DB

    def show_gambar(self, row, col):
        if col != 1:  # hanya kolom Part Number
            return
        try:
            part_number = self.table.item(row, 1).text()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT gambar FROM data_part WHERE `part number` = ?", (part_number,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                pixmap = QPixmap()
                pixmap.loadFromData(result[0])

                # Buat popup dialog
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Gambar - {part_number}")
                dialog.setModal(True)

                vbox = QVBoxLayout(dialog)
                label = QLabel()
                label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
                label.setAlignment(Qt.AlignCenter)
                vbox.addWidget(label)

                # --- Tombol aksi ---
                btn_layout = QHBoxLayout()

                # Tombol Simpan
                save_btn = QPushButton("💾 Simpan Gambar")
                def save_image():
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "Simpan Gambar", f"{part_number}.png", "Images (*.png *.jpg)"
                    )
                    if file_path:
                        pixmap.save(file_path)
                        QMessageBox.information(self, "Sukses", f"Gambar disimpan di:\n{file_path}")
                save_btn.clicked.connect(save_image)
                btn_layout.addWidget(save_btn)

                # Tombol Edit/Ganti
                edit_btn = QPushButton("✏️ Ganti Gambar")
                def edit_image():
                    file_name, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar Baru", "", "Images (*.png *.jpg *.jpeg)")
                    if file_name:
                        with open(file_name, "rb") as f:
                            new_image_data = f.read()
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE data_part SET gambar = ? WHERE `part number` = ?",
                                (new_image_data, part_number)
                            )
                            conn.commit()
                            conn.close()

                            # Update langsung label di popup
                            new_pixmap = QPixmap()
                            new_pixmap.loadFromData(new_image_data)
                            label.setPixmap(new_pixmap.scaled(400, 400, Qt.KeepAspectRatio))

                            QMessageBox.information(self, "Sukses", "Gambar berhasil diganti!")

                            # Refresh tabel (jika ada gambar indikator di kolom tertentu)
                            self.load_part_list()
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Gagal mengganti gambar: {e}")
                edit_btn.clicked.connect(edit_image)
                btn_layout.addWidget(edit_btn)

                vbox.addLayout(btn_layout)
                dialog.setLayout(vbox)
                dialog.resize(450, 500)
                dialog.exec_()
            else:
                QMessageBox.information(self, "Info", "Tidak ada gambar untuk part ini.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menampilkan gambar: {e}")


