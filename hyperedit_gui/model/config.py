from common_py.config import Config

_CONFIG_SINGLETON = None

class HeConfig(Config):

    def __init__(self) -> None:
        super().__init__('hyperedit_gui')
        self.observers = []

    def AddObserver(self, observer):
        self.observers.append(observer)

    def NotifyObservers(self):
        for observer in self.observers:
            observer.OnConfigUpdate()

    def _PrepareSave(self):
        return dict()

    def _DefaultConfig(self):
        return dict()
    
def GetConfig():
    global _CONFIG_SINGLETON
    if not _CONFIG_SINGLETON:
        _CONFIG_SINGLETON = HeConfig()
    return _CONFIG_SINGLETON
