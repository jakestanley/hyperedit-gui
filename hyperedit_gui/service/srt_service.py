import os

from hyperedit.deaggress import deaggress
from hyperedit_gui.observable import Observable
from hyperedit_gui.model.projects import GetCurrentProject
from hyperedit_gui.model.srt import LoadSrts, GetSrts, SaveEdits

import hyperedit_gui.service.tracks_service as ts
from hyperedit_gui.service.project_service import GetProjectService

_SINGLETON = None

class SrtService(Observable):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("SrtService MUST not be instantiated more than once")
        super().__init__()
        self._deaggress_seconds = 0
        GetProjectService().AddObserver(self)

    def NotifyObserver(self, observer):
        return observer.OnSrtChange()
    
    def OnProjectChange(self):
        LoadSrts(self.GetSrtFilePath())
        self.NotifyObservers()
    
    def SetDeaggressSeconds(self, value):
        self._deaggress_seconds = value

    def SetEnabled(self, enabled, indices = [], notify=False):
        for index in indices:
            GetSrts()[index].enabled = enabled
            GetSrts()[index].NotifyObservers()

        SaveEdits(self.GetDeaggressedSrtFilePath()) # TODO: inefficient, need a callback

    def SetEditedStart(self, value, index):
        GetSrts()[index].edited_start_time = value
        SaveEdits(self.GetDeaggressedSrtFilePath())

    def SetEditedEnd(self, value, index):
        GetSrts()[index].edited_end_time = value
        SaveEdits(self.GetDeaggressedSrtFilePath())

    def GetSrtFilePath(self):

        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_directory = os.path.join(project_directory, "SRT")

        return os.path.join(srt_directory, f"{ts.GetTracksService().GetTracksBitmap()}.srt")

    def GetDeaggressedSrtFilePath(self):

        if self._deaggress_seconds == 0:
            return self.GetSrtFilePath()

        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_directory = os.path.join(project_directory, "SRT")

        deaggress_seconds_ms = int(self._deaggress_seconds * 1000)
        srt_file_path = os.path.join(srt_directory, f"{ts.GetTracksService().GetTracksBitmap()}-d{deaggress_seconds_ms}ms.srt")
 
        return srt_file_path

    def CanDeaggress(self):
        return self._deaggress_seconds > 0

    def GetDeaggressSeconds(self):
        return self._deaggress_seconds

    def Deaggress(self):
        input_path = self.GetSrtFilePath()
        output_path = self.GetDeaggressedSrtFilePath()
        if input_path == output_path:
            print("Error: input and output paths are the same")
            return
        # TODO change deaggress to throw a named exception and handle and continue
        try:
            # TODO fix bug: deaggress and merge seems to cut off the first
            deaggress(input_path, self._deaggress_seconds, True, output_path)
        except Exception as e:
            print(f"Error deaggressing (possibly already exists): {e}")
        print(f"Deaggressed to {output_path}")
        LoadSrts(output_path)
        self.NotifyObservers()

    def DeaggressZero(self):
        if self._deaggress_seconds == 0:
            return
        self._deaggress_seconds = 0
        LoadSrts(self.GetSrtFilePath())
        self.NotifyObservers()

def GetSrtService() -> SrtService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = SrtService()
    return _SINGLETON
