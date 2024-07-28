import os
import platform
import subprocess

from hyperedit.split_video import split, concat
from hyperedit_gui.model.projects import GetCurrentProject

_SINGLETON = None

class RenderService:
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("RenderService MUST not be instantiated more than once")
        self._play_after_render = False # TODO: store in config?
        self._render_preview = True # TODO: store in project

    def OpenRenderFolder(self):
        project_directory = os.path.dirname(GetCurrentProject().project_path)
        render_directory = os.path.join(project_directory, "RENDER")
        os.startfile(render_directory)

    def SetRenderPreview(self, enabled):
        self._render_preview = enabled

    def SetPlayAfterRender(self, enabled):
        self._play_after_render = enabled

    # TODO: if any clips are corrupt, this breaks. this can be caused by stopping the app mid split
    def Render(self, srts):

        if len(srts) == 0:
            print("No SRTs to render")
            return

        project_directory = os.path.dirname(GetCurrentProject().project_path)
        clip_directory = os.path.join(project_directory, "CLIP")
        render_directory = os.path.join(project_directory, "RENDER")

        gpu_platform = "nvidia"
        if platform.system() == "Darwin":
            gpu_platform = "apple"
        
        files = split(
            srts=srts,
            original_video_file_path=GetCurrentProject().video_path,
            output_directory=clip_directory,
            preview=self._render_preview,
            overwrite=False,
            gpu=gpu_platform
        )

        final_output = concat(
            srts=srts,
            original_video_file_path=GetCurrentProject().video_path,
            output_directory=render_directory,
            preview=False,
            overwrite=False,
            gpu=gpu_platform,
            files=files
        )

        # TODO do not block
        if self._play_after_render:
            subprocess.run(["ffplay", final_output])

def GetRenderService() -> RenderService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = RenderService()
    return _SINGLETON
