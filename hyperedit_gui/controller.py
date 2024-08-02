import os
import subprocess

from hyperedit.transcribe import transcribe

from hyperedit_gui.model.projects import Project, GetCurrentProject, GlanceProject
from hyperedit_gui.model.recent_projects import GetRecentProjects
from hyperedit_gui.view.files import FindProjectFile, FindVideoFile

from hyperedit_gui.service.project_service import GetProjectService
from hyperedit_gui.service.tracks_service import GetTracksService
from hyperedit_gui.service.srt_service import GetSrtService

class Controller:
    def __init__(self):
        self._transcribe_observers = []

    def AddTranscribeObserver(self, observer):
        self._transcribe_observers.append(observer)

    def NotifyTranscribeObservers(self):
        for observer in self._transcribe_observers:
            observer.OnTranscribe()

    def CreateProject(self, video_file_path):
        GetProjectService().CreateProject(video_file_path)
    
    def LoadProject(self, project_path):
        GetProjectService().LoadProject(project_path)
    
    def RemoveProject(self, project_path):
        GetRecentProjects().RemoveRecentProject(project_path)

    def locate_files(self, project: Project):
        old_project_path = project.project_path
        if not project.IsProjectPathValid():
            project.project_path = FindProjectFile(project.name)
            project = GlanceProject(project.project_path)
        if not project.IsVideoPathValid():
            project.video_path = FindVideoFile(project.video_path)
        project.Save()
        GetRecentProjects().ReplaceRecentProject(old_project_path, project.project_path)

    def GetTracks(self):
        return GetTracksService().GetTracks()
    
    def CanMergeTracks(self):
        if not GetCurrentProject():
            return False
        return any(GetCurrentProject().tracks)        
    
    def AreTracksMerged(self):
        return GetTracksService().AreTracksMerged()
    
    def AreTracksTranscribed(self):
        return GetTracksService().AreTracksTranscribed()
    
    def MergeTracks(self): # TODO: fix bug where transcribe button is not automatically enabled when merge complete
        GetTracksService().MergeTracks()

    def TranscribeTracks(self): # TODO: fix bug where SRTs are not automatically selected when transcribe complete (similar to above)
                                #   workaround is to reload the project
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_file = GetSrtService().GetSrtFilePath()
        wav_directory = os.path.join(project_directory, "WAV")
        audio_file_path = os.path.join(wav_directory, f"{GetTracksService().GetTracksBitmap()}.wav")     
        transcribe(audio_file_path, srt_file)
        self.NotifyTranscribeObservers()

    def ToggleTrack(self, index, state):
        GetTracksService().ToggleTrack(index, state)

    def DeaggressZero(self):
        GetSrtService().DeaggressZero()

    def PreviewTrack(self, index):
        GetTracksService().PreviewTrack(index)
