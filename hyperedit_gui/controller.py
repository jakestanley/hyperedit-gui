import os
import subprocess

from hyperedit.extract_dialog import get_audio_tracks, extract_dialog
from hyperedit.transcribe import transcribe
from hyperedit.srt import parse_srt, PreviewSrt
from hyperedit.deaggress import deaggress
from hyperedit_gui.config import GetConfig
from hyperedit_gui.projects import CreateProject, ReadProject
from pathlib import Path

class Controller:
    def __init__(self):
        self._current_project = None
        self._deaggress_seconds = 0

        self._current_project_observers = []
        self._srt_observers = []

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

    def SelectSrt(self):
        self.NotifySrtChangeObservers()
    
    def read_projects(self):
        return GetConfig().ReadRecentProjects()
    
    def GetTracksBitmap(self):
        bitmap = 0
        for index, value in enumerate(self._current_project.tracks):
            if value:
                bitmap |= (1 << index)
        return bitmap

    def GetTracks(self):
        if self._current_project.tracks:
            return self._current_project.tracks
        self._current_project.tracks = [False for track in get_audio_tracks(self._current_project.video_path)]
        return self._current_project.tracks
    
    def CanMergeTracks(self):
        if not self._current_project:
            return False
        return any(self._current_project.tracks)        
    
    def AreTracksMerged(self):
        if not self._current_project:
            return False
        project_directory = os.path.dirname(self._current_project.project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")
        return os.path.exists(merge_file)
    
    def AreTracksTranscribed(self):
        if not self._current_project:
            return False

        srt_file = self.GetSrtFilePath()
        return os.path.exists(srt_file)
    
    def MergeTracks(self):
        project_directory = os.path.dirname(self._current_project.project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        tracks = [index for index, value in enumerate(self.GetTracks()) if value]   
        extract_dialog(self._current_project.video_path, tracks, merge_file)

    def TranscribeTracks(self):
        project_directory = os.path.dirname(self._current_project.project_path)
        srt_file = self.GetSrtFilePath()
        wav_directory = os.path.join(project_directory, "WAV")
        audio_file_path = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        transcribe(audio_file_path, srt_file)
        self.NotifySrtChangeObservers()

    def GetSrtFilePath(self, deaggress_seconds=None):

        if deaggress_seconds is None:
            deaggress_seconds = self._deaggress_seconds

        project_directory = os.path.dirname(self._current_project.project_path)
        srt_directory = os.path.join(project_directory, "SRT")
        if deaggress_seconds == 0: # no deaggressing
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}.srt")
        else:
            deaggress_seconds = int(deaggress_seconds * 1000)
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}-d{deaggress_seconds}ms.srt")
        return srt_file_path

    def GetSrt(self):
        return parse_srt(self.GetSrtFilePath())

    def ToggleTrack(self, index, state):
        self._current_project.tracks[index] = state
        self._current_project.Save()
        self.NotifyProjectChangeObservers()

    def PreviewSrt(self, index):
        print(f"Previewing srt {index}")
        srt = self.GetSrt()[int(index)-1]

        video_path = Path(self._current_project.video_path)
        PreviewSrt(video_path=str(video_path), srt=srt)

    def SetDeaggressSeconds(self, value):
        self._next_deaggress_seconds = value

    def GetDeaggressSeconds(self):
        return self._deaggress_seconds

    # TODO save changes
    def Deaggress(self):
        input_path = self.GetSrtFilePath()
        output_path = self.GetSrtFilePath(self._next_deaggress_seconds)
        # TODO change deaggress to throw a named exception and handle and continue
        try:
            # TODO fix bug: deaggress and merge seems to cut off the first
            deaggress(input_path, self._deaggress_seconds, False, output_path)
        except Exception as e:
            print(f"Error deaggressing (possibly already exists): {e}")
        print(f"Deaggressed to {output_path}")
        self._deaggress_seconds = self._next_deaggress_seconds
        self.NotifySrtChangeObservers()
        

    def PreviewTrack(self, index):
        print(f"Previewing track {index}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", self._current_project.video_path,
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

        self._current_project.video_path
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