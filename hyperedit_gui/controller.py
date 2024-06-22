import os
import subprocess

from hyperedit.extract_dialog import get_audio_tracks, extract_dialog
from hyperedit.transcribe import transcribe
from hyperedit.srt import parse_srt, PreviewSrt
from hyperedit.deaggress import deaggress
from hyperedit_gui.config import GetConfig
from hyperedit_gui.projects import CreateProject, GetCurrentProject, ReadProject, LoadProject
from hyperedit_gui.recent_projects import RecentProjects
from pathlib import Path

class Controller:
    def __init__(self):
        self._deaggress_seconds = 0
        self._current_project_observers = []
        self._srt_observers = []
        self._recent_projects = RecentProjects()

    def AddProjectChangeObserver(self, observer):
        self._current_project_observers.append(observer)

    def AddSrtChangeObserver(self, observer):
        self._srt_observers.append(observer)

    def NotifyProjectChangeObservers(self):
        for observer in self._current_project_observers:
            observer.OnProjectChange()

    def NotifySrtChangeObservers(self):
        for observer in self._srt_observers:
            observer.OnSrtChange()

    def create_project(self, video_file_path):
        
        try:
            CreateProject(video_file_path)
            GetConfig().AddRecentProject(GetCurrentProject().project_path)
            GetConfig().Save()
            self.NotifyProjectChangeObservers()
        except Exception as e:
            print(f"Failed to create project: {e}")
            return
    
    def load_project(self, project_path):
        LoadProject(project_path)
        self.NotifyProjectChangeObservers()
    
    def remove_project(self, project_path):
        GetConfig().RemoveRecentProject(project_path)
        GetConfig().Save()

    def SelectSrt(self):
        self.NotifySrtChangeObservers()
    
    def ReadRecentProjects(self):
        return self._recent_projects.ReadProjects()
    
    def GetTracksBitmap(self):
        bitmap = 0
        for index, value in enumerate(GetCurrentProject().tracks):
            if value:
                bitmap |= (1 << index)
        return bitmap

    def GetTracks(self):
        if GetCurrentProject().tracks:
            return GetCurrentProject().tracks
        GetCurrentProject().tracks = [False for track in get_audio_tracks(GetCurrentProject().video_path)]
        return GetCurrentProject().tracks
    
    def CanMergeTracks(self):
        if not GetCurrentProject():
            return False
        return any(GetCurrentProject().tracks)        
    
    def AreTracksMerged(self):
        if not GetCurrentProject():
            return False
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")
        return os.path.exists(merge_file)
    
    def AreTracksTranscribed(self):
        if not GetCurrentProject():
            return False

        srt_file = self.GetSrtFilePath()
        return os.path.exists(srt_file)
    
    def MergeTracks(self):
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        tracks = [index for index, value in enumerate(self.GetTracks()) if value]   
        extract_dialog(GetCurrentProject().video_path, tracks, merge_file)

    def TranscribeTracks(self):
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_file = self.GetSrtFilePath()
        wav_directory = os.path.join(project_directory, "WAV")
        audio_file_path = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        transcribe(audio_file_path, srt_file)
        self.NotifySrtChangeObservers()

    def GetSrtFilePath(self, deaggress_seconds=0):

        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_directory = os.path.join(project_directory, "SRT")
        if deaggress_seconds is 0: # no deaggressing
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}.srt")
        else:
            deaggress_seconds = int(deaggress_seconds * 1000)
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}-d{deaggress_seconds}ms.srt")
        return srt_file_path

    def GetSrt(self):
        return parse_srt(self.GetSrtFilePath(self._deaggress_seconds))

    def ToggleTrack(self, index, state):
        GetCurrentProject().tracks[index] = state
        GetCurrentProject().Save()
        self.NotifyProjectChangeObservers()

    def PreviewSrt(self, index):
        print(f"Previewing srt {index}")

        # subtract 1 because the collection is zero indexed. this may be wrong
        srt = self.GetSrt()[int(index)-1]

        video_path = Path(GetCurrentProject().video_path)
        PreviewSrt(video_path=str(video_path), srt=srt)

    def SetDeaggressSeconds(self, value):
        self._deaggress_seconds = value

    def DeaggressZero(self):
        self._deaggress_seconds = 0
        self.NotifySrtChangeObservers()

    def GetDeaggressSeconds(self):
        return self._deaggress_seconds

    def Deaggress(self):
        input_path = self.GetSrtFilePath()
        output_path = self.GetSrtFilePath(self._deaggress_seconds)
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
        self._deaggress_seconds = self._deaggress_seconds
        self.NotifySrtChangeObservers()
        

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