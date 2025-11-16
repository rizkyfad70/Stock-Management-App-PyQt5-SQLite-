from PyQt5.QtWidgets import ( 
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QComboBox, QDateEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget, QFrame, QFormLayout, QCompleter
)
from PyQt5.QtCore import QDate, pyqtSignal, Qt, QStringListModel
from PyQt5.QtGui import QFont, QColor
import sqlite3
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stok.db')

class StokInPage(QWidget):
    stok_updated = pyqtSignal()
    part_added = pyqtSignal()
    lokasi_added = pyqtSignal()

    def __init__(self, pic):
        super().__init__()
        self.pic = pic
        self.setup_ui()

        # terapkan style global setelah widget dibuat
        self.setStyleSheet(self._global_style())
        self.load_part_names()
        self.load_stok_in_table()
        self.load_lokasi()
        self.load_stok_act()

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
        header = QLabel("📥 Form Stok Masuk")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white; 
            background-color: #3b82f6; padding: 10px; border-radius: 6px;
        """)
        root_layout.addWidget(header)

        welcome_label = QLabel(f"Silahkan isi data dengan benar, {self.pic}!")
        root_layout.addWidget(welcome_label)

                # ---------------- Main Layout ----------------
        main_layout = QVBoxLayout()
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

        # Part Name 
        self.part_name_input = QLineEdit()
        self.part_name_input.textChanged.connect(self.update_part_numbers)

        form_layout.addRow(QLabel("Pilih Nama Part:"), self.part_name_input)

        # Part Number ComboBox
        self.part_number_combo = QComboBox()
        self.part_number_combo.currentTextChanged.connect(self.update_part_info)
        form_layout.addRow(QLabel("Pilih Part Number:"), self.part_number_combo)

        # Kategori ComboBox
        self.kategori_combo = QComboBox()
        form_layout.addRow(QLabel("Kategori:"), self.kategori_combo)

        # Mesin ComboBox
        self.mesin_combo = QComboBox()
        form_layout.addRow(QLabel("Mesin:"), self.mesin_combo)

        # Qty Input
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Masukkan jumlah barang masuk")
        form_layout.addRow(QLabel("Jumlah (Qty):"), self.qty_input)

        # Lokasi ComboBox
        self.lokasi_combo = QComboBox()
        # load_lokasi dipanggil nanti setelah style diterapkan / di __init__
        form_layout.addRow(QLabel("Pilih Lokasi Penyimpanan:"), self.lokasi_combo)

        # Tanggal
        self.tanggal_input = QDateEdit()
        self.tanggal_input.setDate(QDate.currentDate())
        self.tanggal_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Tanggal Masuk:"), self.tanggal_input)

        # Tombol Simpan
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Simpan Stok Masuk")
        self.save_btn.clicked.connect(self.simpan_stok)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        form_layout.addRow(btn_row)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)  # beri proporsi

        # ---------------- Tab untuk tabel ----------------
        self.tabs = QTabWidget()

        # Tab Part
        stok_in_tab = QWidget()
        part_layout = QVBoxLayout(stok_in_tab)

        # search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari part...")
        self.search_input.textChanged.connect(self.filter_active_table)
        part_layout.addWidget(self.search_input)

        # Tabel Stok Masuk
        self.stok_in_table = QTableWidget()
        self.stok_in_table.setColumnCount(8)
        self.stok_in_table.setHorizontalHeaderLabels(["Part Name", "Part Number", "Mesin", "Kategori", "Lokasi", "Tanggal", "Qty In", "PIC"])
        self.stok_in_table.setSortingEnabled(True)
        self.stok_in_table.verticalHeader().setVisible(False)
        self.stok_in_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stok_in_table.setStyleSheet("""
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
        self.stok_in_table.setFont(font)
        self.stok_in_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
        part_layout.addWidget(self.stok_in_table)
        self.tabs.addTab(stok_in_tab, "📋 Log Stock In")

        # Tabel log Stok out
        stok_out_tab = QWidget()
        stok_out_layout = QVBoxLayout(stok_out_tab)

        # search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari part...")
        self.search_input.textChanged.connect(self.filter_active_table)
        stok_out_layout.addWidget(self.search_input)

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
        
        stok_out_layout.addWidget(self.stok_out_table)
        self.tabs.addTab(stok_out_tab, "🛠️ Log Stock Out")

        # Tab Stok Act
        stok_act_tab = QWidget()
        stok_act_layout = QVBoxLayout(stok_act_tab)

        # search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari part...")
        self.search_input.textChanged.connect(self.filter_active_table)
        stok_act_layout.addWidget(self.search_input)

        self.stok_act = QTableWidget()
        self.stok_act.setColumnCount(6)
        self.stok_act.setHorizontalHeaderLabels(["Part Name", "Part Number", "Mesin", "Kategori", "Lokasi", "Qty"])
        self.stok_act.setSortingEnabled(True)
        self.stok_act.verticalHeader().setVisible(False)
        self.stok_act.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stok_act.setStyleSheet("""
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
        self.stok_act.setFont(font)
        self.stok_act.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
        stok_act_layout.addWidget(self.stok_act)
        self.tabs.addTab(stok_act_tab, "📦 Stok Aktual")


        # ----------------- Tambahkan Tabs ke Main Layout -----------------
        main_layout.addWidget(self.tabs, 2)
        # ----------------- Tambahkan Tabs ke Main Layout -----------------
        main_layout.addWidget(self.tabs, 3)

        # Tombol Export CSV
        export_btn = QPushButton("⬇️ Export CSV")
        export_btn.clicked.connect(self.export_csv)
        main_layout.addWidget(export_btn)

        # Load data tabel (fungsi harus ada)
        self.load_stok_in_table()
        self.load_stok_out_table()
        self.load_stok_act()



    def load_part_names(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT "part name" FROM data_part')
            names = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Perbarui model autocompletion
            model = QStringListModel(names)
            completer = QCompleter()
            completer.setModel(model)
            completer.setCaseSensitivity(False)
            self.part_name_input.setCompleter(completer)

        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat nama part: {e}")

    def update_part_numbers(self, part_name):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT "part number" FROM data_part WHERE "part name" = ?', (part_name,))
            numbers = cursor.fetchall()
            conn.close()

            self.part_number_combo.clear()
            for num in numbers:
                self.part_number_combo.addItem(num[0])

        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat part number: {e}")

    def update_part_info(self, part_number):
        try:
            part_name = self.part_name_input.text()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT kategori, mesin FROM data_part WHERE "part number" = ? AND "part name" = ?',
                (part_number, part_name)
            )
            results = cursor.fetchall()
            conn.close()
            self.kategori_combo.clear()
            self.mesin_combo.clear()
            kategori_list = []
            mesin_list = []
            for row in results:
                kategori_list.append(row[0])
                mesin_list.append(row[1])
            self.kategori_combo.addItems(list(set(kategori_list)))
            self.mesin_combo.addItems(list(set(mesin_list)))
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat info part: {e}")

    def load_lokasi(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT lokasi FROM lokasi")
            lokasi_list = cursor.fetchall()
            conn.close()

            self.lokasi_combo.clear()
            for item in lokasi_list:
                self.lokasi_combo.addItem(item[0])
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat lokasi: {e}")

    def load_stok_in_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT "part name", "part number", mesin, kategori, lokasi, tanggal, qty_in, pic
                FROM stok_in
            """)
            rows = cursor.fetchall()
            conn.close()
            self.stok_in_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                for column_index, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    # Atur alignment ke tengah untuk kolom tertentu
                    if column_index in [2, 3, 4, 5, 6, 7]:  # "part number", "qty_in", "pic"
                        item.setTextAlignment(Qt.AlignCenter)
                    self.stok_in_table.setItem(row_index, column_index, item)
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal memuat tabel stok_in: {e}")
    def filter_active_table(self, text):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            table = self.stok_in_table
        elif current_tab == 1:
            table = self.stok_out_table
        else:
            table = self.stok_act

        for row in range(table.rowCount()):
            match = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            table.setRowHidden(row, not match)

    
    def simpan_stok(self):
        part_name = self.part_name_input.text()
        part_number = self.part_number_combo.currentText()
        mesin = self.mesin_combo.currentText()
        kategori = self.kategori_combo.currentText()
        qty = self.qty_input.text()
        lokasi = self.lokasi_combo.currentText()
        tanggal = self.tanggal_input.date().toString("yyyy-MM-dd")

        if not qty or not part_name or not part_number or not mesin or not lokasi:
            QMessageBox.warning(self, "Input Salah", "Semua kolom wajib diisi!")
            return

        if not qty.isdigit() or int(qty) <= 0:
            QMessageBox.warning(self, "Input Salah", "Qty harus berupa angka > 0!")
            return

        qty_int = int(qty)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stok_in ("part number", "part name", kategori, mesin, qty_in, lokasi, tanggal, pic)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (part_number, part_name, kategori, mesin, qty_int, lokasi, tanggal, self.pic))
            
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sukses", f"Stok oleh '{self.pic}' berhasil disimpan.")
            # clear input (dont close page)
            self.qty_input.clear()
            self.tanggal_input.setDate(QDate.currentDate())
            self.part_name_input.clear()
            self.part_number_combo.clear()
            self.kategori_combo.clear()
            self.mesin_combo.clear()

            # reset combobox ke index pertama jika ada item
            if self.part_number_combo.count() > 0:
                self.part_number_combo.setCurrentIndex(0)
            if self.mesin_combo.count() > 0:
                self.mesin_combo.setCurrentIndex(0)
            if self.kategori_combo.count() > 0:
                self.kategori_combo.setCurrentIndex(0)
            if self.lokasi_combo.count() > 0:
                self.lokasi_combo.setCurrentIndex(0)

            # emit signal supaya dashboard refresh
            self.load_stok_in_table()
            self.load_stok_act()
            self.stok_updated.emit()
            self.part_added.emit()
            self.lokasi_added.emit()

        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menyimpan data: {e}")

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
                        item = QTableWidgetItem(str(value))
                        # Atur alignment ke tengah untuk kolom tertentu
                        if column_index in [2, 3, 4, 5, 6, 7]:  # "part number", "qty_in", "pic"
                            item.setTextAlignment(Qt.AlignCenter)
                        self.stok_out_table.setItem(row_index, column_index, item)
            except Exception as e:
                QMessageBox.critical(self, "Gagal", f"Gagal memuat tabel stok_out: {e}")

    def load_stok_act(self):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT "part name", "part number", mesin, kategori, lokasi, qty_blc
                    FROM balance
                """)
                rows = cursor.fetchall()
                conn.close()
                self.stok_act.setRowCount(len(rows))
                for row_index, row in enumerate(rows):
                    for column_index, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        # Atur alignment ke tengah untuk kolom tertentu
                        if column_index in [2, 3, 4, 5]:  # "part number", "qty_in", "pic"
                            item.setTextAlignment(Qt.AlignCenter)
                        self.stok_act.setItem(row_index, column_index, item)
            except Exception as e:
                QMessageBox.critical(self, "Gagal", f"Gagal memuat tabel stok_act: {e}")

    def export_csv(self):
        # Pilih file untuk simpan
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return  # user cancel

        # Cek tab aktif
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            table = self.stok_in_table
        elif current_tab == 1:
            table = self.stok_out_table
        else:
            table = self.stok_act

        # Tulis data ke CSV
        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # header
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            writer.writerow(headers)

            # isi tabel
            for row in range(table.rowCount()):
                rowdata = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    rowdata.append(item.text() if item else "")
                writer.writerow(rowdata)

        QMessageBox.information(self, "Export CSV", f"Data berhasil disimpan ke:\n{path}")
