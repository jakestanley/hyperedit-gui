from hyperedit_gui.service.observable_service import ObservableService

_SINGLETON = None

class SrtService(ObservableService):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("SrtService MUST only be instantiated once")
        super().__init__()

    def NotifyObserver(self, observer):
        observer.OnSrtChange()

    def PostConstruct(self):
        pass

    def OnProjectChange(self):
        pass

def GetSrtService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = SrtService()
    return _SINGLETON