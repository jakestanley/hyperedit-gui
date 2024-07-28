import os
import subprocess

from hyperedit_gui.observable import Observable

from hyperedit_gui.model.projects import GetCurrentProject
from hyperedit_gui.service.srt_service import GetSrtService

from hyperedit.extract_dialog import get_audio_tracks, extract_dialog

_SINGLETON = None

class TracksService(Observable):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("TracksService MUST not be instantiated more than once")
        super().__init__()

    def NotifyObserver(self, observer):
        return observer.OnMerge()

    def GetTracks(self):
        if GetCurrentProject().tracks:
            return GetCurrentProject().tracks
        GetCurrentProject().tracks = [False for track in get_audio_tracks(GetCurrentProject().video_path)]
        return GetCurrentProject().tracks

    def GetTracksBitmap(self):
        bitmap = 0

        if not GetCurrentProject().tracks:
            return bitmap

        for index, value in enumerate(GetCurrentProject().tracks):
            if value:
                bitmap |= (1 << index)

        return bitmap
    
    def PreviewTrack(self, index):
        print(f"Previewing track {index}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", GetCurrentProject().video_path,
            "-map", f"0:a:{index}",
            "-t", "10",
            "-af", "acompressor, silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB",
            "-f", "wav",
            "-",
        ]

        ffplay_cmd = [
            "ffplay",
            "-autoexit", "-t", "10", # to prevent ffplay continuing to read from the pipe after ffmpeg is done
            "-nodisp",
            "-"
        ]

        GetCurrentProject().video_path
        # TODO stop button
        # this works in cmd
        # ffmpeg -y -i ".\2024-06-16 20-59-05.mkv" -map 0:a:1 -af "acompressor, silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB" -f wav - | ffplay -nodisp -
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)

        # Second command
        ffplay_process = subprocess.Popen(ffplay_cmd, stdin=ffmpeg_process.stdout)

        # Ensure the first process's output is passed to the second process
        ffplay_process.wait()

        # Get the final output
        output, error = ffplay_process.communicate()

    def ToggleTrack(self, index, enabled):
        # TODO move me
        GetCurrentProject().tracks[index] = enabled
        GetCurrentProject().Save()
        self.NotifyObservers()
    
    def AreTracksMerged(self):
        if not GetCurrentProject():
            return False
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{GetTracksService().GetTracksBitmap()}.wav")
        return os.path.exists(merge_file)

    def AreTracksTranscribed(self):
        if not GetCurrentProject():
            return False

        srt_file = GetSrtService().GetSrtFilePath()
        return os.path.exists(srt_file)
    
    def MergeTracks(self):
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{GetTracksService().GetTracksBitmap()}.wav")     
        tracks = [index for index, value in enumerate(self.GetTracks()) if value]   
        extract_dialog(GetCurrentProject().video_path, tracks, merge_file)
        self.NotifyObservers()

def GetTracksService() -> TracksService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = TracksService()
    return _SINGLETON
