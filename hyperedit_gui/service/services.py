from typing import List

from hyperedit_gui.service.observable_service import ObservableService
from hyperedit_gui.service.project_service import GetProjectService
from hyperedit_gui.service.srt_service import GetSrtService
from hyperedit_gui.service.transcribe_service import GetTranscribeService
from hyperedit_gui.service.merge_service import GetMergeService
from hyperedit_gui.service.render_service import GetRenderService

def InitialiseServices():

    services: List[ObservableService] = [
        GetProjectService(),
        GetSrtService(),
        GetTranscribeService(),
        GetMergeService(),
        GetRenderService()
    ]

    # any observers for these services can now be safely set
    for service in services:
        service.PostConstruct()