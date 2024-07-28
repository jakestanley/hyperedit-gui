import os

from hyperedit_gui.service.observable_service import ObservableService
from hyperedit_gui.model.projects import GetCurrentProject
from hyperedit.extract_dialog import get_audio_tracks, extract_dialog

_SINGLETON = None

class MergeService(ObservableService):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("MergeService MUST only be instantiated once")
        super().__init__()

    def MergeTracks(self): # TODO: fix bug where transcribe button is not automatically enabled when merge complete
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        tracks = [index for index, value in enumerate(self.GetTracks()) if value]   
        extract_dialog(GetCurrentProject().video_path, tracks, merge_file)
        self.NotifyMergeObservers()

    def NotifyObserver(self, observer):
        observer.OnMerge()

    def PostConstruct(self):
        pass

def GetMergeService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = MergeService()
    return _SINGLETON