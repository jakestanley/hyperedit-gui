from common_py.config import Config

_RECENT_PROJECTS_SINGLETON = None
_MAX_PROJECTS = 20

class RecentProjects(Config):
    def __init__(self):
        super().__init__('hyperedit_gui', 'recent_projects')
        self._projects = self.config["projects"]
        self.observers = []

    def TouchProject(self, project):
        self._projects.remove(project)
        self._projects.append(project)
        self.Save()

    def AddObserver(self, observer):
        self.observers.append(observer)

    def NotifyObservers(self):
        for observer in self.observers:
            observer.OnRecentProjectsUpdate()
    
    def AddRecentProject(self, project):
        if project in self._projects:
            self.TouchProject(project)
        else:
            self._projects.append(project)
        if len(self._projects) > _MAX_PROJECTS:
            self._projects.pop(0)
        self.Save()
        self.NotifyObservers()
        return project
    
    def GetRecentProjectPaths(self):
        # because we append to a list, to have recent at the top we must 
        #   reverse the list before returning it
        return reversed(self._projects)
    
    def RemoveRecentProject(self, project):
        self._projects.remove(project)
        self.Save()
        self.NotifyObservers()

    def ReplaceRecentProject(self, old_project, new_project):
        self._projects.remove(old_project)
        self._projects.append(new_project)
        self.Save()
        self.NotifyObservers()

    def _PrepareSave(self):
        return dict(
            projects=self._projects
        )

    def _DefaultConfig(self):
        return dict(
            projects=[]
        )

def GetRecentProjects():
    global _RECENT_PROJECTS_SINGLETON
    if not _RECENT_PROJECTS_SINGLETON:
        _RECENT_PROJECTS_SINGLETON = RecentProjects()
    return _RECENT_PROJECTS_SINGLETON