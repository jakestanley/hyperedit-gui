import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, \
    QWidget, QHBoxLayout, QLabel, QListWidgetItem, QListWidget

from PySide6.QtCore import Qt

from hyperedit_gui.model.projects import Project, GlanceRecentProjects
from hyperedit_gui.controller import Controller
from hyperedit_gui.model.config import GetConfig
from hyperedit_gui.model.recent_projects import GetRecentProjects
from hyperedit_gui.view.files import FindProjectFile, FindVideoFile

from hyperedit_gui.service.project_service import GetProjectService

class RecentProjectWidget(QWidget):
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
        self.pathLabel = QLabel(self.project.project_path)
        if self.project.IsProjectPathValid():
            self.pathLabel.setStyleSheet("font-size: 12px; color: grey;")
        else:
            self.pathLabel.setStyleSheet("font-size: 12px; color: red;")

        # video path label
        self.videoLabel = QLabel(self.project.video_path if self.project.video_path else "No file available")
        if self.project.IsVideoPathValid():
            self.videoLabel.setStyleSheet("font-size: 12px; color: grey;")
        else:
            self.videoLabel.setStyleSheet("font-size: 12px; color: red;")

        # Open button
        self.openButton = QPushButton("Open")
        self.openButton.setMaximumWidth(80)
        self.openButton.clicked.connect(self.open_project)
        self.openButton.setEnabled(self.project.IsValid())

        # Locate
        self.locateButton = QPushButton("Locate")
        self.locateButton.setMaximumWidth(80)
        self.locateButton.clicked.connect(self.locate_files)
        self.locateButton.setEnabled(not self.project.IsValid())

        # Remove button
        removeButton = QPushButton("Remove")
        removeButton.setMaximumWidth(80)
        removeButton.clicked.connect(self.remove_project)

        # Setup layouts
        vLayout.addWidget(nameLabel)
        vLayout.addWidget(self.pathLabel)
        vLayout.addWidget(self.videoLabel)
        hLayout.addLayout(vLayout)
        hLayout.addWidget(self.openButton, alignment=Qt.AlignRight)
        hLayout.addWidget(self.locateButton)
        hLayout.addWidget(removeButton)
        self.setLayout(hLayout)

    def open_project(self):
        GetProjectService().LoadProject(self.project.project_path)

    def remove_project(self):
        GetRecentProjects().RemoveRecentProject(self.project.project_path)

    def locate_files(self):
        # this will cause this widget to be deleted and recreated
        self.controller.locate_files(self.project)

class ProjectWindow(QWidget):

    def __init__(self, parent, controller: Controller):
        super().__init__(parent)

        self.controller = controller
        GetProjectService().AddObserver(self)
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
        GetRecentProjects().AddObserver(self)
        self.populateList()

    def populateList(self):

        self.listWidget.clear()
        for project in GlanceRecentProjects():
            listItem = QListWidgetItem(self.listWidget)
            projectWidget = RecentProjectWidget(project, self.controller)
            listItem.setSizeHint(projectWidget.sizeHint())
            if project.IsValid():
                listItem.setFlags(listItem.flags() & ~Qt.ItemIsSelectable)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, projectWidget)

    def newProject(self):
        self.controller.CreateProject(FindVideoFile())

    def loadProject(self):
        self.controller.LoadProject(FindProjectFile())

    def OnRecentProjectsUpdate(self):
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
