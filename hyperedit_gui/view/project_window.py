import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QVBoxLayout, QPushButton, QWidget, QTableView, QStyledItemDelegate, QHBoxLayout, QLabel, QListWidgetItem, QListWidget
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import QCoreApplication, Qt

class ProjectWidget(QWidget):
    def __init__(self, name, path):
        super().__init__()
        self.name = name
        self.path = path
        self.initUI()
    
    def initUI(self):
        # Layouts
        # vLayout = QVBoxLayout(self)
        
        hLayout = QHBoxLayout(self)
        hLayout.setContentsMargins(8, 8, 8, 8)

        # Project name label
        vLayout = QVBoxLayout(self)
        nameLabel = QLabel(self.name)
        nameLabel.setStyleSheet("font-size: 14px;")

        # Project path label
        pathLabel = QLabel(self.path)
        pathLabel.setStyleSheet("font-size: 12px; color: grey;")

        # Open button
        openButton = QPushButton("Open")
        openButton.setMaximumWidth(80)
        # openButton.clicked.connect(self.openProject)

        # Setup layouts
        vLayout.addWidget(nameLabel)
        vLayout.addWidget(pathLabel)
        hLayout.addLayout(vLayout)
        # hLayout.addWidget(openButton, alignment=Qt.AlignRight)
        hLayout.addWidget(openButton)
        self.setLayout(hLayout)

class ProjectWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window's size
        self.resize(600, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(QPushButton("New project"))
        self.layout.addWidget(QPushButton("Load project"))
        
        self.listWidget = QListWidget()
        self.layout.addWidget(self.listWidget)
        # self.setCentralWidget(self.listWidget)
        self.populateList()

    def populateList(self):
        projects = [
            ("Project Alpha", "/path/to/alpha"),
            ("Project Beta", "/path/to/beta"),
            ("Project Gamma", "/path/to/gamma")
        ]
        for name, path in projects:
            listItem = QListWidgetItem(self.listWidget)
            projectWidget = ProjectWidget(name, path)
            listItem.setSizeHint(projectWidget.sizeHint())
            listItem.setFlags(listItem.flags() & ~Qt.ItemIsSelectable)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, projectWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectWindow()
    window.show()
    sys.exit(app.exec())
