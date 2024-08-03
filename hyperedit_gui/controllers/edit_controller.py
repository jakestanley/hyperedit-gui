from hyperedit.srt import PreviewSrt

from hyperedit_gui.model.srt import GetSrts
from hyperedit_gui.model.projects import Project, GetCurrentProject
from hyperedit_gui.service.player_service import PlayerService, GetPlayerService
from hyperedit_gui.service.edl_service import EDLService, GetEDLService
from hyperedit_gui.service.tracks_service import TracksService, GetTracksService
from hyperedit_gui.service.render_service import RenderService, GetRenderService
from hyperedit_gui.service.srt_service import GetSrtService

_SINGLETON = None

class EditController:
    """
    This controller orchestrates logic for the Edit (SRT) window
    """
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("EditController MUST not be instantiated more than once")
        self._selected_rows = []

    def SetSrtRowEnabled(self, index, enabled):
        GetSrtService().SetEnabled(enabled, [int(index)-1])

    def SetSelectedSrtRows(self, selected_rows):
        self._selected_rows = selected_rows
        texts = []
        for index, row in enumerate(self._selected_rows):
            texts.append((index, GetSrts()[int(row)].text))
        return 

    def SetSrtEditedStart(self, row, value: float):
        GetSrtService().SetEditedStart(value, int(row))

    def SetSrtEditedEnd(self, row, value: float):
        GetSrtService().SetEditedStart(value, int(row))

    def SetDeaggressSeconds(self, value):
        GetSrtService().SetDeaggressSeconds(value)

    def GetDeaggressSeconds(self):
        return GetSrtService().GetDeaggressSeconds()

    def CanDeaggress(self):
        return GetSrtService().CanDeaggress()

    # TODO move to SrtService
    def DeaggressZero(self):
        GetSrtService().DeaggressZero()

    def _SetSelectedEnabled(self, enabled):
        GetSrtService().SetEnabled(enabled, self._selected_rows)

    def EnableSelected(self):
        self._SetSelectedEnabled(True)

    def DisableSelected(self):
        self._SetSelectedEnabled(False)

    def SetRenderPreview(self, enabled):
        GetRenderService().SetRenderPreview(enabled)

    def SetPlayAfterRender(self, enabled):
        GetRenderService().SetPlayAfterRender(enabled)

    def OpenRenderFolder(self):
        GetRenderService().OpenRenderFolder()

    def RenderAll(self):
        GetRenderService().Render([srt.to_primitive() for srt in GetSrts()])

    def RenderEnabled(self): # TODO do not re-concatenate if file with hash exists, i.e replaying a render
        GetRenderService().Render([srt.to_primitive() for srt in GetSrts() if srt.enabled])

    def _GetSelectedEnabledPrimitives(self):
        srts = []
        for row in self._selected_rows:
            srt = GetSrts()[int(row)]
            if srt.enabled:
                srts.append(srt.to_primitive())
        return srts

    def RenderEnabledSelection(self):
        GetRenderService().Render(self._GetSelectedEnabledPrimitives())

    def Deaggress(self):
        GetSrtService().Deaggress()

    def PreviewFine(self, index):
        video_path = GetCurrentProject().video_path

        # subtract 1 because the collection is zero indexed. this may be wrong
        srt = GetSrts()[int(index)-1]

        PreviewSrt(video_path=str(video_path), srt=srt.to_primitive(), player='mpv')

    def PreviewSelected(self):
        video_path = GetCurrentProject().video_path

        srts = []
        for row in self._selected_rows:
            srt = GetSrts()[int(row)]
            srts.append(srt.to_primitive())

        GetPlayerService().Preview(video_path, srts)    

    def PreviewSelectedEnabled(self):
        video_path = GetCurrentProject().video_path
        GetPlayerService().Preview(video_path, self._GetSelectedEnabledPrimitives())

    def CreateEdl(self):
        GetEDLService().CreateEDL()

def GetEditController() -> EditController:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = EditController()
    return _SINGLETON
