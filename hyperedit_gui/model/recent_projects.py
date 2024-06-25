from hyperedit_gui.model.config import GetConfig
from hyperedit_gui.model.projects import ReadProject

_MAX_PROJECTS = 10

class RecentProjects:
    def __init__(self):
        self._projects = GetConfig().GetRecentProjectPaths()
        self.observers = []

    def AddObserver(self, observer):
        self.observers.append(observer)

    def NotifyObservers(self):
        for observer in self.observers:
            observer.OnConfigUpdate()

    def add_project(self, project):
        if project in self._projects:
            self.touch_project(project)
        else:
            self._projects.append(project)
        if len(self._projects) > _MAX_PROJECTS:
            self._projects.pop(0)

    def touch_project(self, project):
        self._projects.remove(project)
        self._projects.append(project)

    def remove_project(self, project):
        self._projects.remove(project)

    def ReadProjects(self):
        return [ 
            ReadProject(project) for project in self._projects
        ]
    
    def AddRecentProject(self, project):
        rs = self._projects.add_project(project)
        self.NotifyObservers()
        return rs
    
    def RemoveRecentProject(self, project):
        # TODO touch_project interaction
        rs = self._projects.remove_project(project)
        self.NotifyObservers()
        return rs
