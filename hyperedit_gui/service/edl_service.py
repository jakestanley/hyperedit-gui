import os

from hyperedit.time import seconds_to_hmsm
from hyperedit_gui.model.projects import GetCurrentProject
from hyperedit_gui.service.srt_service import GetSrts
from hyperedit_gui.service.tracks_service import GetTracksService

_SINGLETON = None

class EDLService:
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("EDLService MUST not be instantiated more than once")
        pass

    # TODO: provide frame rate (use FFprobe)
    # TODO: move into hyperedit
    def _FormatSecondsToTimeCode(self, seconds, frame_rate):
        """Converts time in seconds to HH:MM:SS:FF format given a frame rate."""
        f_hours = int(seconds // 3600)
        f_minutes = int((seconds % 3600) // 60)
        f_seconds = int(seconds % 60)
        f_frames = int((seconds % 1) * frame_rate)
        return f"{f_hours:02}:{f_minutes:02}:{f_seconds:02}:{f_frames:02}"

    def _GetEDLFilePath(self):
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        edl_directory = os.path.join(project_directory, "EDL")
        return os.path.join(edl_directory, f"test.edl")

    # TODO: not great for Davinci Resolve but MAY be useful for MPV (fine preview en masse)
    def CreateEDL(self):

        clip_name = GetCurrentProject().video_path
        edl_content = f"TITLE: {clip_name}_EDL\nFCM: NON-DROP FRAME\n\n"

        srts = [srt.to_primitive() for srt in GetSrts() if srt.enabled]
        # TODO apparently MPV supports EDL??? https://en.wikipedia.org/wiki/Edit_decision_list
        # Adding time ranges to the EDL
        for idx, (_, start, end, _) in enumerate(srts, start=1):
            start_tc = self._FormatSecondsToTimeCode(start, 60)
            end_tc = self._FormatSecondsToTimeCode(end, 60)
            edl_content += f"{idx:03}  AX       V     C        {start_tc} {end_tc} {start_tc} {end_tc}\n"
            for i in range(len(GetTracksService().GetTracks())):
                edl_content += f"{idx:03}  AX       A{i+1}    C        {start_tc} {end_tc} {start_tc} {end_tc}\n"
            edl_content += f"* FROM CLIP NAME:  {clip_name}\n\n"

        edl_file_path = self._GetEDLFilePath()
        with open(edl_file_path, 'w') as file:
            file.write(edl_content)

def GetEDLService() -> EDLService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = EDLService()
    return _SINGLETON
