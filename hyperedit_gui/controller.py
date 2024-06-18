import os
import json

from PySide6.QtWidgets import QInputDialog

from hyperedit_gui.config import GetConfig, HeConfig

class Controller:
    def __init__(self):
        pass

    # TODO: project class
    def create_project(self, video_file_path):
        directory = os.path.dirname(video_file_path)
        basename, ext = os.path.splitext(os.path.basename(video_file_path))
        if ext.startswith("."):
            ext = ext[1:]
        project_name = f"{basename}_{ext}"

        # a small bit of ui here isn't toooo bad
        # TODO need to do a directory insert select instead
        project_name, ok = QInputDialog.getText(None, "Project Name", "Enter a project name:", text=project_name)
        if not ok:
            return False

        project_folder = os.path.join(directory, project_name)
        try:
            os.makedirs(project_folder, exist_ok=False)
        except FileExistsError:
            return False
        
        subdirectories = [ "WAV", "SRT", "CLIP" ]
        for subdir in subdirectories:
            os.makedirs(os.path.join(project_folder, subdir), exist_ok=True)

        project_file_path = os.path.join(project_folder, "project.json")
        with open(project_file_path, "w") as project_file:
            project = {}
            project["file"] = video_file_path
            project["name"] = project_name
            # project["tracks"] = self.tracks
            json.dump(project, project_file, indent=4)

        GetConfig().projects.add_project(project_file_path)
        GetConfig().Save()
        return project
    
    def load_project(self, project_path):
        return False
    
    def remove_project(self, project_path):
        print("remove project2 called")
        GetConfig().projects.remove_project(project_path)
        GetConfig().Save()
    
    def read_projects(self):
        return GetConfig().projects.read_projects()

