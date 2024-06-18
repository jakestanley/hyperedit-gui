import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, \
    QWidget, QHBoxLayout, QLabel, QListWidgetItem, QListWidget, \
    QFileDialog

from PySide6.QtCore import Qt

from hyperedit_gui.projects import Project
from hyperedit_gui.controller import Controller
from hyperedit_gui.config import GetConfig, HeConfig

class ProjectWidget(QWidget):
    def __init__(self, project: Project, controller: Controller):
        super().__init__()
        self.project = project
        self.controller = controller
        self.initUI()
    
    def initUI(self):
        
        hLayout = QHBoxLayout(self)
        hLayout.setContentsMargins(8, 8, 8, 8)

        # Project name label
        vLayout = QVBoxLayout(self)
        nameLabel = QLabel(self.project.name)
        nameLabel.setStyleSheet("font-size: 14px;")

        # Project path label
        pathLabel = QLabel(self.project.name)
        pathLabel.setStyleSheet("font-size: 12px; color: grey;")

        # Open button
        openButton = QPushButton("Open")
        openButton.setMaximumWidth(80)
        openButton.clicked.connect(self.open_project)

        # Remove button
        removeButton = QPushButton("Remove")
        removeButton.setMaximumWidth(80)
        removeButton.clicked.connect(self.remove_project)

        # Setup layouts
        vLayout.addWidget(nameLabel)
        vLayout.addWidget(pathLabel)
        hLayout.addLayout(vLayout)
        hLayout.addWidget(openButton, alignment=Qt.AlignRight)
        hLayout.addWidget(removeButton)
        self.setLayout(hLayout)

    def open_project(self):
        self.controller.load_project(self.project.project_path)

    def remove_project(self):
        self.controller.remove_project(self.project.project_path)

class ProjectWindow(QWidget):

    def __init__(self, parent, controller: Controller):
        super().__init__(parent)

        self.controller = controller
        self.controller.AddProjectChangeObserver(self)
        GetConfig().AddObserver(self)

        # Set the main window's size
        self.resize(800, 600)

        self.layout = QVBoxLayout(self)
        new_project_button = QPushButton("New project")
        new_project_button.clicked.connect(self.newProject)
        self.layout.addWidget(new_project_button)
        load_project_button = QPushButton("Load project")
        load_project_button.clicked.connect(self.loadProject)
        self.layout.addWidget(load_project_button)
        
        self.listWidget = QListWidget()
        self.layout.addWidget(self.listWidget)
        self.populateList()

    def populateList(self):

        self.listWidget.clear()
        for project in self.controller.read_projects():
            listItem = QListWidgetItem(self.listWidget)
            projectWidget = ProjectWidget(project, self.controller)
            listItem.setSizeHint(projectWidget.sizeHint())
            listItem.setFlags(listItem.flags() & ~Qt.ItemIsSelectable)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, projectWidget)

    def newProject(self):
        print("New project...")
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)", options=options)
        if fileName:
            self.controller.create_project(fileName)

    def loadProject(self):
        print("Loading project...")
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()", "",
            "Video or Project Files (*.json *.mp4 *.avi *.mov *.mkv);;All Files (*)", options=options)
        if fileName:
            self.controller.load_project(fileName)

    def OnConfigUpdate(self):
        self.populateList()

    def OnProjectChange(self):
        self.parent().setCurrentIndex(1)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    projects = [
        ("Project Alpha", "/path/to/alpha"),
        ("Project Beta", "/path/to/beta"),
        ("Project Gamma", "/path/to/gamma")
    ]

    config: HeConfig = GetConfig()
    window = ProjectWindow(parent=None, controller=Controller())
    window.show()
    sys.exit(app.exec())
