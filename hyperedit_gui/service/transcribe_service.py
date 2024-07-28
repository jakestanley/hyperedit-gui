import os

from hyperedit_gui.service.observable_service import ObservableService
from hyperedit_gui.model.projects import GetCurrentProject
from hyperedit.transcribe import transcribe

_SINGLETON = None

class TranscribeService(ObservableService):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("TranscribeService MUST only be instantiated once")
        super().__init__()

    def NotifyObserver(self, observer):
        observer.OnTranscribe()

    def PostConstruct(self):
        pass

    def TranscribeTracks(self): # TODO: fix bug where SRTs are not automatically selected when transcribe complete (similar to above)
                                #   workaround is to reload the project
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_file = self.GetSrtFilePath()
        wav_directory = os.path.join(project_directory, "WAV")
        audio_file_path = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        transcribe(audio_file_path, srt_file)
        self.NotifyObservers()

def GetTranscribeService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = TranscribeService()
    return _SINGLETON