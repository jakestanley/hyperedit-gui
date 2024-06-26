import os
import subprocess
import platform

from hyperedit.extract_dialog import get_audio_tracks, extract_dialog
from hyperedit.transcribe import transcribe
from hyperedit.srt import PreviewSrt, GetPrimitiveSrtListHash
from hyperedit.deaggress import deaggress
from hyperedit.split_video import split_video
from hyperedit_gui.model.config import GetConfig
from hyperedit_gui.model.srt import LoadSrts, GetSrts, SaveEdits
from hyperedit_gui.model.projects import CreateProject, GetCurrentProject, LoadProject
from hyperedit_gui.model.recent_projects import RecentProjects
from pathlib import Path

class Controller:
    def __init__(self):
        self._deaggress_seconds = 0
        self._selected_rows = []
        self._current_project_observers = []
        self._srt_observers = []
        self._merge_observers = []
        self._play_after_render = False # TODO: store in config?
        self._render_preview = True # TODO: store in project
        self._recent_projects = RecentProjects()

    def AddProjectChangeObserver(self, observer):
        self._current_project_observers.append(observer)

    def AddMergeObserver(self, observer):
        self._merge_observers.append(observer)

    def AddSrtChangeObserver(self, observer):
        self._srt_observers.append(observer)

    def NotifyProjectChangeObservers(self):
        for observer in self._current_project_observers:
            observer.OnProjectChange()

    def NotifyMergeObservers(self):
        for observer in self._merge_observers:
            observer.OnMerge()

    def NotifySrtChangeObservers(self):
        for observer in self._srt_observers:
            observer.OnSrtChange()

    def create_project(self, video_file_path):
        
        try:
            CreateProject(video_file_path)
            self._recent_projects.add_project(GetCurrentProject().project_path)
            GetConfig().Save()
            self.NotifyProjectChangeObservers()
        except Exception as e:
            print(f"Failed to create project: {e}")
            return
    
    def load_project(self, project_path):
        LoadProject(project_path)
        LoadSrts(self.GetSrtFilePath())
        self.NotifyProjectChangeObservers()
    
    def remove_project(self, project_path):
        GetConfig().RemoveRecentProject(project_path)
        GetConfig().Save()
    
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
    
    def MergeTracks(self): # TODO: fix bug where transcribe button is not automatically enabled when merge complete
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        wav_directory = os.path.join(project_directory, "WAV")
        merge_file = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        tracks = [index for index, value in enumerate(self.GetTracks()) if value]   
        extract_dialog(GetCurrentProject().video_path, tracks, merge_file)

    def TranscribeTracks(self): # TODO: fix bug where SRTs are not automatically selected when transcribe complete (similar to above)
                                #   workaround is to reload the project
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_file = self.GetSrtFilePath()
        wav_directory = os.path.join(project_directory, "WAV")
        audio_file_path = os.path.join(wav_directory, f"{self.GetTracksBitmap()}.wav")     
        transcribe(audio_file_path, srt_file)
        self.NotifyTranscribeObservers()
        self.NotifySrtChangeObservers()

    def GetSrtFilePath(self, deaggress_seconds=0):
        """
        Get SRT file path for deaggress seconds. If edits, edit file is also returned
        """

        # TODO: this should probably be a member of Project
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_directory = os.path.join(project_directory, "SRT")
        if deaggress_seconds == 0: # no deaggressing
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}.srt")
        else:
            deaggress_seconds = int(deaggress_seconds * 1000)
            srt_file_path = os.path.join(srt_directory, f"{self.GetTracksBitmap()}-d{deaggress_seconds}ms.srt")
 
        return srt_file_path

    def ToggleTrack(self, index, state):
        GetCurrentProject().tracks[index] = state
        GetCurrentProject().Save()
        self.NotifyProjectChangeObservers()

    def PreviewSrt(self, index):
        print(f"Previewing srt {index}")

        # subtract 1 because the collection is zero indexed. this may be wrong
        srt = GetSrts()[int(index)-1]

        video_path = Path(GetCurrentProject().video_path)
        PreviewSrt(video_path=str(video_path), srt=srt.to_primitive(), player='mpv')

    def SetSrtRowEnabled(self, index, enabled):
        print(f"Setting srt row {index} enabled to {enabled}")
        GetSrts()[int(index)-1].enabled = enabled
        SaveEdits(self.GetSrtFilePath(self._deaggress_seconds)) # inefficient

    def SetDeaggressSeconds(self, value):
        self._deaggress_seconds = value

    def DeaggressZero(self):
        if self._deaggress_seconds == 0:
            return
        self._deaggress_seconds = 0
        LoadSrts(self.GetSrtFilePath())
        self.NotifySrtChangeObservers()

    def SetSelectedSrtRows(self, selected_rows):
        self._selected_rows = selected_rows

    def _SetSelectedEnabled(self, enabled):
        for row in self._selected_rows:
            GetSrts()[int(row)].enabled = enabled
        print(f"Computed hash for enabled SRTs: {GetPrimitiveSrtListHash([srt.to_primitive() for srt in GetSrts() if srt.enabled])}")

    def EnableSelected(self):
        self._SetSelectedEnabled(True)
        self.NotifySrtChangeObservers()

    def DisableSelected(self):
        self._SetSelectedEnabled(False)
        self.NotifySrtChangeObservers()

    def SetRenderPreview(self, enabled):
        self._render_preview = enabled

    def SetPlayAfterRender(self, enabled):
        self._play_after_render = enabled

    def GetDeaggressSeconds(self):
        return self._deaggress_seconds
# TODO: deaggress or merge must ignore disabled clips
# TODO: render with deaggress option



    def _Render(self, srts): # TODO: if any clips are corrupt, this breaks. this can be caused by stopping the app mid split

        if len(srts) == 0:
            print("No SRTs to render")
            return

        project_directory = os.path.dirname(GetCurrentProject().project_path)
        srt_directory = os.path.join(project_directory, "CLIP")

        # split_video(srt_file_path=self.GetSrtFilePath(self._deaggress_seconds),
        gpu_platform = "nvidia"
        if platform.system() == "Darwin":
            gpu_platform = "apple"
        
        final_output = split_video(srt_file_path=None,
                    srts=srts,
                    video_file_path=GetCurrentProject().video_path,
                    output_directory=srt_directory,
                    preview=self._render_preview,
                    overwrite=False,
                    range=None,
                    gpu=gpu_platform
        )
        if self._play_after_render:
            subprocess.run(["ffplay", final_output])

    def RenderAll(self):
        self._Render([srt.to_primitive() for srt in GetSrts()])

    def RenderEnabled(self): # TODO do not re-concatenate if file with hash exists, i.e replaying a render
        self._Render([srt.to_primitive() for srt in GetSrts() if srt.enabled])

    def RenderEnabledSelection(self):
        srts = []
        for row in self._selected_rows:
            srt = GetSrts()[int(row)]
            if srt.enabled:
                srts.append(srt.to_primitive())

        self._Render(srts)

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
        LoadSrts(output_path)
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
