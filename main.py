from PyQt6 import QtCore, QtGui, QtWidgets
import json

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(935, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.calendarWidget = QtWidgets.QCalendarWidget(parent=self.centralwidget)
        self.calendarWidget.setGeometry(QtCore.QRect(10, 10, 711, 570))
        self.calendarWidget.setObjectName("calendarWidget")
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader) # Menghilangkan header vertikal
        self.textBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(730, 10, 191, 331))
        self.textBrowser.setObjectName("textBrowser")

        # Tambahkan QTextBrowser baru di bawah textBrowser yang pertama
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(730, 370, 191, 131))
        self.textBrowser_2.setObjectName("textBrowser_2")

        # Tambahkan tombol tambah catatan ke dalam textBrowser
        self.addButton = QtWidgets.QPushButton("Tambah Catatan", self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(730, 510, 191, 31))
        self.removeButton = QtWidgets.QPushButton("Hapus Catatan", self.centralwidget)
        self.removeButton.setGeometry(QtCore.QRect(730, 550, 191, 31))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class AddEventWindow(QtWidgets.QDialog):
    def __init__(self, date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Agenda dan Warna")

        self.layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel(f"Agenda untuk {date.toString()}:")
        self.textEdit = QtWidgets.QTextEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.textEdit)

        self.colorButton = QtWidgets.QPushButton("Pilih Warna")
        self.colorButton.clicked.connect(self.set_color)
        self.layout.addWidget(self.colorButton)

        self.addButton = QtWidgets.QPushButton("Tambah")
        self.addButton.clicked.connect(self.add_event)
        self.layout.addWidget(self.addButton)

        self.removeButton = QtWidgets.QPushButton("Hapus Agenda")
        self.removeButton.clicked.connect(self.remove_event)
        self.layout.addWidget(self.removeButton)

        self.setLayout(self.layout)

        self.date = date
        self.color = QtGui.QColor()

        # Memeriksa apakah ada keterangan yang sudah tersimpan untuk tanggal ini
        event_date_str = date.toString(QtCore.Qt.DateFormat.ISODate)
        if event_date_str in parent.events:
            event = parent.events[event_date_str]
            self.textEdit.setPlainText(event.get('agenda', ''))
            color_name = event.get('warna', '')
            if color_name:
                self.color = QtGui.QColor(color_name)

    # Fungsi lain tetap sama seperti sebelumnya

    def set_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color = color

    def add_event(self):
        event = {
            'agenda': self.textEdit.toPlainText(),
            'warna': self.color.name() # Mengambil nama warna sebagai string
        }
        self.parent().set_event(self.date, event)
        self.accept()

    def remove_event(self):
        self.parent().remove_event(self.date)
        self.accept()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.events = {}
        self.notes = []

        self.load_data()

        self.ui.calendarWidget.selectionChanged.connect(self.update_text_browser)
        self.ui.calendarWidget.setGridVisible(True)
        self.ui.calendarWidget.paintCell = self.paint_cell

        # Mengubah warna tanggal di luar bulan yang dipilih menjadi abu-abu
        self.ui.calendarWidget.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

        # Menambahkan event untuk menangani double click pada sel kalender
        self.ui.calendarWidget.activated.connect(self.open_add_event_window)

        # Menambahkan event untuk menangani button tambah catatan
        self.ui.addButton.clicked.connect(self.add_note)

        # Menambahkan event untuk menangani button hapus catatan
        self.ui.removeButton.clicked.connect(self.remove_note)

        # Menampilkan catatan yang tersimpan saat aplikasi dibuka
        self.display_notes()

    def open_add_event_window(self, date):
        add_event_window = AddEventWindow(date, self)
        add_event_window.exec()

    def add_note(self):
        note, ok_pressed = QtWidgets.QInputDialog.getText(self, "Tambah Catatan", "Masukkan Catatan:")
        if ok_pressed:  # Check if OK button is clicked
            current_text = self.ui.textBrowser_2.toPlainText()
            new_text = f"{current_text}\n{note}"
            self.ui.textBrowser_2.setPlainText(new_text)
            self.notes.append(note)  # Menambahkan catatan baru ke dalam list
            self.save_data()

    def remove_note(self):
        self.ui.textBrowser_2.clear()  # Remove all text from the second textBrowser
        self.notes.clear()  # Clear the notes list
        self.save_data()  # Save the cleared notes list to JSON

    def set_event(self, date, event):
        self.events[date.toString(QtCore.Qt.DateFormat.ISODate)] = event # Menggunakan tanggal sebagai kunci dalam penyimpanan event
        self.save_data()
        self.ui.calendarWidget.update()
        self.update_text_browser()  # Update teks browser setelah menambahkan event

    def remove_event(self, date):
        date_str = date.toString(QtCore.Qt.DateFormat.ISODate)
        if date_str in self.events:
            del self.events[date_str]
            self.save_data()
            self.ui.calendarWidget.update()
            self.update_text_browser()  # Update teks browser setelah menghapus event

    def update_text_browser(self):
        date = self.ui.calendarWidget.selectedDate()
        month = date.month()
        year = date.year()
        keterangan = ""
        for event_date_str, event in self.events.items():
            event_date = QtCore.QDate.fromString(event_date_str, QtCore.Qt.DateFormat.ISODate)
            if event_date.month() == month and event_date.year() == year and event['agenda'] != "":
                keterangan += f"Tanggal {event_date.day()} : {event['agenda']}\n\n"
        self.ui.textBrowser.setText(f"Agenda:\n{keterangan}")

    def paint_cell(self, painter, rect, date):
        event_date_str = date.toString(QtCore.Qt.DateFormat.ISODate)
        if event_date_str in self.events:
            color = QtGui.QColor(self.events[event_date_str]['warna']) # Mengambil warna dari string
            painter.fillRect(rect, color)

        # Gambar teks angka tanggal di setiap sel kalender
        text = str(date.day())
        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)

    def load_data(self):
        try:
            with open('asset/json/events.json', 'r') as f:
                self.events = json.load(f)
        except FileNotFoundError:
            pass

        try:
            with open('asset/json/notes.json', 'r') as f:
                self.notes = json.load(f)
        except FileNotFoundError:
            pass

    def save_data(self):
        with open('asset/json/events.json', 'w') as f:
            json.dump(self.events, f)

        with open('asset/json/notes.json', 'w') as f:
            json.dump(self.notes, f)

    def display_notes(self):
        for note in self.notes:
            current_text = self.ui.textBrowser_2.toPlainText()
            new_text = f"{current_text}\n{note}"
            self.ui.textBrowser_2.setPlainText(new_text)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
