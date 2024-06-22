import os
import json

from PySide6.QtWidgets import QInputDialog

from hyperedit_gui.exception.exceptions import ProjectException

_PROJECT_SINGLETON = None

_KEY_PROJECT_NAME="name"
_KEY_VIDEO_FILE="video_file"
_KEY_TRACKS="tracks"

class Project:
    def __init__(self, name, project_path, video_path, tracks=None) -> None:
        self.name = name
        self.project_path = project_path
        self.video_path = video_path
        self.tracks = tracks

    def Save(self):
        with open(self.project_path, "w") as project_file:
            config = {}
            config[_KEY_PROJECT_NAME] = self.name
            config[_KEY_VIDEO_FILE] = self.video_path
            config[_KEY_TRACKS] = self.tracks
            json.dump(config, project_file, indent=4)

def GetCurrentProject() -> Project:
    global _PROJECT_SINGLETON
    return _PROJECT_SINGLETON

def CreateProject(video_file_path):
    global _PROJECT_SINGLETON

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

    _PROJECT_SINGLETON = Project(project_name, project_file_path, video_file_path, None)
    _PROJECT_SINGLETON.Save()

def ReadProject(project_path) -> Project:
    """
    Read minimal project information and return. Intended for use with RecentProjects
    """
    try:
        with open(project_path, 'r') as project_file:
            project_json = json.load(project_file)
            return Project(project_json.get(_KEY_PROJECT_NAME, "<NO NAME>"), project_path, project_json.get(_KEY_VIDEO_FILE, "missing"), project_json.get(_KEY_TRACKS, None))
    except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
        raise ProjectException(f"Project file not found: {project_path}")

def LoadProject(project_path):
    """
    Load project into singleton instance
    """
    global _PROJECT_SINGLETON
    _PROJECT_SINGLETON = None

    try:
        with open(project_path, 'r') as project_file:
            project_json = json.load(project_file)
            _PROJECT_SINGLETON = Project(project_json.get(_KEY_PROJECT_NAME, "<NO NAME>"), project_path, project_json.get(_KEY_VIDEO_FILE, "missing"), project_json.get(_KEY_TRACKS, None))
    except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
        raise ProjectException(f"Project file not found: {project_path}")
