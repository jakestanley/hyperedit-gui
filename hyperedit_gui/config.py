from common_py.config import Config

_CONFIG_SINGLETON = None

class HeConfig(Config):

    def __init__(self) -> None:
        super().__init__('hyperedit_gui')
        self._projects = self.config["projects"]
        self.observers = []

    def AddObserver(self, observer):
        self.observers.append(observer)

    def NotifyObservers(self):
        for observer in self.observers:
            observer.OnConfigUpdate()

    def GetRecentProjectPaths(self):
        return self._projects
    
    def SetRecentProjectPaths(self, recent_projects):
        for project in recent_projects.GetProjects():
            self._projects.append(project.path)

    def _PrepareSave(self):
        return dict(
            projects=self._projects
        )

    def _DefaultConfig(self):
        return dict(
            projects=[]
        )
    
def GetConfig():
    global _CONFIG_SINGLETON
    if not _CONFIG_SINGLETON:
        _CONFIG_SINGLETON = HeConfig()
    return _CONFIG_SINGLETON
