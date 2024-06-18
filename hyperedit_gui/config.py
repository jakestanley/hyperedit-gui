from common_py.config import Config
from hyperedit_gui.projects import RecentProjects

_CONFIG_SINGLETON = None

class HeConfig(Config):

    def __init__(self) -> None:
        super().__init__('hyperedit_gui')
        self._observers = []
        self._projects = RecentProjects(self.config["projects"])

    def AddObserver(self, observer):
        self._observers.append(observer)

    def NotifyObservers(self):
        for observer in self._observers:
            observer.OnConfigUpdate()

    def ReadRecentProjects(self):
        return self._projects.read_projects()
    
    def AddRecentProject(self, project):
        rs = self._projects.add_project(project)
        self.NotifyObservers()
        return rs
    
    def RemoveRecentProject(self, project):
        # TODO touch_project interaction
        rs = self._projects.remove_project(project)
        self.NotifyObservers()
        return rs

    def _PrepareSave(self):
        return dict(
            projects=self._projects.projects
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
