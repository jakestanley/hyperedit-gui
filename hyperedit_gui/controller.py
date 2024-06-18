import os
import json

from PySide6.QtWidgets import QInputDialog

from hyperedit.extract_dialog import get_audio_tracks
from hyperedit_gui.config import GetConfig
from hyperedit_gui.projects import CreateProject, ReadProject

class Controller:
    def __init__(self):
        self._current_project = None
        self._current_project_observers = []

    def AddProjectChangeObserver(self, observer):
        self._current_project_observers.append(observer)

    def NotifyProjectChangeObservers(self):
        for observer in self._current_project_observers:
            observer.OnProjectChange()

    def create_project(self, video_file_path):
        
        project = CreateProject(video_file_path)
        if not project:
            print("Failed to create project")
            return

        GetConfig().AddRecentProject(project.project_path)
        GetConfig().Save()

        self._current_project = project
        self.NotifyProjectChangeObservers()
    
    def load_project(self, project_path):
        self._current_project = ReadProject(project_path)
        self.NotifyProjectChangeObservers()
    
    def remove_project(self, project_path):
        GetConfig().RemoveRecentProject(project_path)
        GetConfig().Save()
    
    def read_projects(self):
        return GetConfig().ReadRecentProjects()
    
    def GetTracks(self):
        return [False for track in get_audio_tracks(self._current_project.video_path)]

    def PreviewTrack(self, index):
        print(f"Previewing track {index}")
        # TODO stop button
        # this works in cmd
        # ffmpeg -y -i ".\2024-06-16 20-59-05.mkv" -map 0:a:1 -af "acompressor, silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB" -f wav - | ffplay -nodisp -