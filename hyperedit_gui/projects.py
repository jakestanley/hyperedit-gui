import os
import json
from typing import List

from PySide6.QtWidgets import QInputDialog

_MAX_PROJECTS = 10

_KEY_PROJECT_NAME="name"
_KEY_VIDEO_FILE="video_file"

class Project:
    def __init__(self, name, project_path, video_path) -> None:
        self.name = name
        self.project_path = project_path
        self.video_path = video_path

    def Save(self):
        print("Saving project (not yet implemented)")
        pass

class RecentProjects:
    def __init__(self, projects=[]):
        self.projects = projects

    def add_project(self, project):
        if project in self.projects:
            self.touch_project(project)
        else:
            self.projects.append(project)
        if len(self.projects) > _MAX_PROJECTS:
            self.projects.pop(0)

    def touch_project(self, project):
        self.projects.remove(project)
        self.projects.append(project)

    def remove_project(self, project):
        self.projects.remove(project)

    def read_projects(self):
        return [ 
            ReadProject(project) for project in self.projects
        ]

def CreateProject(video_file_path) -> Project:

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
        return None
    
    subdirectories = [ "WAV", "SRT", "CLIP" ]
    for subdir in subdirectories:
        os.makedirs(os.path.join(project_folder, subdir), exist_ok=True)

    project_file_path = os.path.join(project_folder, "project.json")
    with open(project_file_path, "w") as project_file:
        project = {}
        project["project_path"] = project_file_path
        project[_KEY_VIDEO_FILE] = video_file_path
        project[_KEY_PROJECT_NAME] = project_name
        # project["tracks"] = self.tracks
        json.dump(project, project_file, indent=4)

        return Project(project_name, project_file_path, video_file_path)

    

def ReadProject(project_path) -> Project:
    try:
        with open(project_path, 'r') as project_file:
            project = json.load(project_file)
            return Project(project.get(_KEY_PROJECT_NAME, "<NO NAME>"), project_path, project.get(_KEY_VIDEO_FILE, "missing"))
    except json.decoder.JSONDecodeError:
        return Project("<INVALID JSON>", project_path)
    except FileNotFoundError:
        return Project("<MISSING>", project_path)

