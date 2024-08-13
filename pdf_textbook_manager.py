import sys
import os
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QListWidget, QFileDialog, QMessageBox, QLabel, QSplitter, QProgressBar)
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QDesktopServices
import fitz  # PyMuPDF

class PDFTextbookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Textbook Manager")
        self.setGeometry(100, 100, 800, 600)

        self.storage_path = os.path.join(os.path.expanduser("~"), "PDFTextbooks")
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        self.init_ui()
        self.apply_custom_style()

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Left side: Buttons and List
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        storage_label = QLabel(f"Textbooks are stored in:\n{self.storage_path}")
        storage_label.setWordWrap(True)
        left_layout.addWidget(storage_label)

        add_button = QPushButton("Add Textbook")
        add_button.clicked.connect(self.add_textbook)
        left_layout.addWidget(add_button)

        self.textbook_list = QListWidget()
        self.textbook_list.itemSelectionChanged.connect(self.display_selected_textbook)
        left_layout.addWidget(self.textbook_list)

        open_button = QPushButton("Open Selected Textbook")
        open_button.clicked.connect(self.open_textbook)
        left_layout.addWidget(open_button)

        left_widget.setLayout(left_layout)

        # Right side: PDF Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.preview_label = QLabel("Select a textbook to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_label)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Indeterminate progress
        self.loading_bar.hide()
        right_layout.addWidget(self.loading_bar)

        right_widget.setLayout(right_layout)

        # Create a splitter and add widgets
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])  # Set initial sizes

        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_listbox()

    def apply_custom_style(self):
        # Set application font
        app_font = QFont("Helvetica", 12)
        QApplication.setFont(app_font)

        # Set color palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)

        # Set stylesheet for more detailed styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a92ea;
            }
            QListWidget {
                background-color: #2a2a2a;
                border: none;
            }
            QLabel {
                color: #ffffff;
            }
        """)

    def add_textbook(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Textbook", "", "PDF Files (*.pdf)")
        if file_path:
            file_name = os.path.basename(file_path)
            destination = os.path.join(self.storage_path, file_name)
            shutil.copy2(file_path, destination)
            QMessageBox.information(self, "Success", f"Added {file_name} to the library")
            self.update_listbox()

    def update_listbox(self):
        self.textbook_list.clear()
        for file in os.listdir(self.storage_path):
            if file.endswith(".pdf"):
                self.textbook_list.addItem(file)

    def display_selected_textbook(self):
        if self.textbook_list.currentItem():
            self.loading_bar.show()
            file_name = self.textbook_list.currentItem().text()
            file_path = os.path.join(self.storage_path, file_name)
            QTimer.singleShot(100, lambda: self.display_pdf_preview(file_path))

    def display_pdf_preview(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)  # Load the first page
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Reduced resolution for faster rendering
            img_data = pix.tobytes("png")  # Convert to PNG format
            
            qimg = QImage()
            qimg.loadFromData(img_data)  # Load the PNG data into QImage
            
            pixmap = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            self.preview_label.setText(f"Error previewing PDF: {str(e)}")
        finally:
            self.loading_bar.hide()

    def open_textbook(self):
        if self.textbook_list.currentItem():
            file_name = self.textbook_list.currentItem().text()
            file_path = os.path.join(self.storage_path, file_name)
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            QMessageBox.warning(self, "Warning", "Please select a textbook to open")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTextbookManager()
    window.show()
    sys.exit(app.exec())