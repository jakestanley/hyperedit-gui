from hyperedit_gui.service.observable_service import ObservableService

_SINGLETON = None

class RenderService(ObservableService):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("RenderService MUST only be instantiated once")
        super().__init__()

    def NotifyObserver(self, observer):
        observer.OnRender()

    def PostConstruct(self):
        pass

def GetRenderService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = RenderService()
    return _SINGLETON