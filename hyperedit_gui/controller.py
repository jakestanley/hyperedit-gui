import os
import json

from PySide6.QtWidgets import QInputDialog

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
            project["video_file"] = video_file_path
            # project["tracks"] = self.tracks
            json.dump(project, project_file, indent=4)

        return True

    def load_project(self, project_file_path):

        with open(project_file_path, "r") as project_file:
            project = json.load(project_file)
        
        # TODO handle IO exceptions etc
        video_file_path = project["video_file"]
        print("Loaded project")
