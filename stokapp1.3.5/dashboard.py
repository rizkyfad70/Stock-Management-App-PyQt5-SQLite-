from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QFrame, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QDialog, QFormLayout, QDialogButtonBox, QFileDialog, QHeaderView, QAbstractItemView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3
import os, csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stok.db')

# ---------------- Dialog Edit Part ----------------
class EditPartDialog(QDialog):
    def __init__(self, part_name, part_number, qty, mesin, kategori, mesin_list=None, kategori_list=None):
        super().__init__()
        self.setWindowTitle(f"Edit {part_name}")
        layout = QFormLayout(self)

        # Input Part Name
        self.name_input = QLineEdit(part_name)
        layout.addRow("Part Name:", self.name_input)

        # Input Part Number
        self.number_input = QLineEdit(part_number)
        layout.addRow("Part Number:", self.number_input)

        # Qty (tidak bisa diedit)
        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 9999)
        self.qty_input.setValue(qty)
        self.qty_input.setReadOnly(True)
        self.qty_input.setButtonSymbols(QSpinBox.NoButtons)
        layout.addRow("Qty (tidak bisa diubah):", self.qty_input)

        # Input Mesin
        self.mesin_combo = QComboBox()
        if mesin_list:
            self.mesin_combo.addItems(mesin_list)
        if mesin in mesin_list:
            self.mesin_combo.setCurrentText(mesin)
        layout.addRow("Mesin:", self.mesin_combo)

        # Input Kategori
        self.kategori_combo = QComboBox()
        if kategori_list:
            self.kategori_combo.addItems(kategori_list)
        if kategori in kategori_list:
            self.kategori_combo.setCurrentText(kategori)
        layout.addRow("Kategori:", self.kategori_combo)

        # Tombol Ok / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.name_input.text(),
            self.number_input.text(),
            self.qty_input.value(),
            self.mesin_combo.currentText(),
            self.kategori_combo.currentText()
        )
    
    

# ---------------- Dashboard ----------------
class Dashboard(QWidget):
    stok_updated = pyqtSignal()

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.min_threshold = 5
        self._setup_ui()
        self.refresh_summary()
        self.load_table()

    # ----------------- UI -----------------
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(15)
        root.setContentsMargins(15,15,15,15)

        # Header
        title = QLabel("📦 Dashboard Stok")
        title.setFont(QFont("Poppins", 20, QFont.Bold))
        title.setStyleSheet("color:#1f2937;")
        welcome = QLabel(f"Selamat datang, {self.username}!")
        welcome.setStyleSheet("color:#4b5563; font-size:14px;")
        root.addWidget(title)
        root.addWidget(welcome)

        # Threshold
        threshold_row = QHBoxLayout()
        threshold_label = QLabel("⚙️ Batas Stok Kritis:")
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 999)
        self.threshold_spin.setValue(self.min_threshold)
        self.threshold_spin.valueChanged.connect(self.update_threshold)
        threshold_row.addWidget(threshold_label)
        threshold_row.addWidget(self.threshold_spin)
        threshold_row.addStretch()
        root.addLayout(threshold_row)

        # ---------------- Kartu Ringkasan ----------------
        self.cards_wrap = QHBoxLayout()
        self.cards_wrap.setSpacing(15)
        root.addLayout(self.cards_wrap)

        self.card_total_part  = self._make_card("📦", "Total Part", "0")
        self.card_qty_part    = self._make_card("📊", "Qty Part", "0")
        self.card_qty_in      = self._make_card("📥", "Qty In", "0")
        self.card_qty_out     = self._make_card("📤", "Qty Out", "0")
        self.card_stok_kritis = self._make_card("⚠️", "Stok Kritis", "0")

        for c in [
            self.card_total_part, self.card_qty_part, self.card_qty_in,
            self.card_qty_out, self.card_stok_kritis
        ]:
            self.cards_wrap.addWidget(c)

                # ---------------- Table & Toolbar ----------------
        table_box = QVBoxLayout()
        table_box.setSpacing(10)

        # Card kecil untuk toolbar
        toolbar_card = QFrame()
        toolbar_card.setStyleSheet("""
            QFrame {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QLabel {
                color:#374151;
                font-size:13px;
            }
            QLineEdit, QComboBox {
                padding: 4px;
                font-size:13px;
            }
            QPushButton {
                padding: 4px 10px;
                border-radius: 6px;
            }
        """)
        toolbar_card.setMaximumHeight(50)  # biar ramping
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari part...")
        self.search_input.textChanged.connect(self.search_table)
        self.search_input.setFixedWidth(200)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Semua", "Stok Kritis", "Tersedia"])
        self.filter_combo.currentIndexChanged.connect(self.load_table)

        btn_export = QPushButton("📤 Export CSV")
        btn_export.setStyleSheet("background-color:#10b981; color:white;")
        btn_export.clicked.connect(self.export_csv)

        toolbar_layout.addWidget(QLabel("🔍 Search:"))
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(QLabel("Filter:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(btn_export)

        # masukkan card ke table_box
        table_box.addWidget(toolbar_card)

        #table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Part Name", "Part Number", "Qty", "Mesin", "Kategori", "Act"
        ])
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Kustomisasi UI tabel
        self.table.setStyleSheet("QTableWidget { border: 1px solid #dcdcdc; }"
                                "QHeaderView::section { background-color: #f0f0f0; border: 1px solid #dcdcdc; padding: 4px; }")

        
        table_box.addWidget(self.table)

        root.addLayout(table_box)


    # ---------------- Card Helper ----------------
    def _make_card(self, icon: str, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #0072ff, stop:1 #00c6ff);
                border-radius: 12px; color: white;
            }
        """)
        card.setMinimumHeight(100)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel(f"{icon} {label}")
        title.setStyleSheet("font-weight:600; font-size:14px;")
        val = QLabel(value)
        val.setFont(QFont("Poppins", 22, QFont.Bold))
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(title)
        layout.addWidget(val)
        card.value_label = val
        return card

    # ---------------- DB ----------------
    def _connect(self):
        return sqlite3.connect(DB_PATH)

    # ---------------- Refresh Summary ----------------
    def update_threshold(self, value):
        self.min_threshold = value
        self.refresh_summary()
        self.load_table()

    def refresh_summary(self):
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM data_part')
            total_part = cur.fetchone()[0] or 0
            cur.execute('SELECT COALESCE(SUM(qty),0) FROM data_part')
            qty_part = cur.fetchone()[0] or 0
            cur.execute('SELECT COALESCE(SUM(qty_in),0) FROM stok_in')
            qty_in = cur.fetchone()[0] or 0
            cur.execute('SELECT COALESCE(SUM(qty_out),0) FROM stok_out')
            qty_out = cur.fetchone()[0] or 0
            cur.execute('SELECT COUNT(*) FROM data_part WHERE qty < ?', (self.min_threshold,))
            stok_kritis = cur.fetchone()[0] or 0
            conn.close()

            self.card_total_part.value_label.setText(str(total_part))
            self.card_qty_part.value_label.setText(str(qty_part))
            self.card_qty_in.value_label.setText(str(qty_in))
            self.card_qty_out.value_label.setText(str(qty_out))
            self.card_stok_kritis.value_label.setText(str(stok_kritis))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat ringkasan: {e}")


    # ---------------- Table ----------------
    def load_table(self):
        try:
            conn = self._connect()
            cur = conn.cursor()
            query = 'SELECT "part name", "part number", COALESCE(qty,0), mesin, kategori FROM data_part'
            params = []
            filter_text = self.filter_combo.currentText()
            if filter_text == "Stok Kritis":
                query += " WHERE COALESCE(qty,0) < ?"
                params.append(self.min_threshold)
            elif filter_text == "Tersedia":
                query += " WHERE COALESCE(qty,0) >= ?"
                params.append(self.min_threshold)
            cur.execute(query, params)
            rows = cur.fetchall()
            conn.close()
            self.display_table(rows)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat tabel: {e}")

    def display_table(self, rows):
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if c_idx in (2,3,4):
                    item.setTextAlignment(Qt.AlignCenter)
                if c_idx == 2 and val < self.min_threshold:  # stok kritis
                    item.setBackground(QColor("#fde68a"))
                self.table.setItem(r_idx, c_idx, item)

            # 🔑 Setelah data masuk, baru resize + stretch
            #self.table.resizeColumnsToContents()
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            #header.setSectionResizeMode(QHeaderView.ResizeToContents)

            # Tombol Hapus
            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background-color:#ef4444;color:white;")
            btn_del.clicked.connect(lambda _, rn=row: self.delete_part(rn))
            self.table.setCellWidget(r_idx, 5, btn_del)

    # ---------------- Search ----------------
    def search_table(self):
        keyword = self.search_input.text().lower()
        try:
            conn = self._connect()
            cur = conn.cursor()
            query = 'SELECT "part name", "part number",COALESCE(qty, 0) as qty, mesin, kategori FROM data_part WHERE LOWER("part name") LIKE ? OR LOWER("part number") LIKE ?'
            cur.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            rows = cur.fetchall()
            conn.close()
            self.display_table(rows)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mencari: {e}")

    def delete_part(self, row):
        part_name, part_number, *_ = row
        reply = QMessageBox.question(self, "Hapus Part",
                                     f"Apakah Anda yakin ingin menghapus {part_name} ({part_number})?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute('DELETE FROM data_part WHERE "part number" = ?', (part_number,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Sukses", f"{part_name} berhasil dihapus")
                self.refresh_summary()
                self.load_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")
# ---------------- Export CSV ----------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                # Header
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount()-1)]  # minus kolom "Act"
                writer.writerow(headers)
                # Isi tabel
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()-1):  # skip kolom Act
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Sukses", f"Data berhasil diexport ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export: {e}")
