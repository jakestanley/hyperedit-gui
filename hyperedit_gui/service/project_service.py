import hyperedit_gui.model.projects as projects

from hyperedit_gui.observable import Observable

_SINGLETON = None

class ProjectService(Observable):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("ProjectService MUST not be instantiated more than once")
        super().__init__()

    # override
    def NotifyObserver(self, observer):
        return observer.OnProjectChange()

    # TODO: projects functionality should be merged into this service class
    def CreateProject(self, video_file_path):
        if video_file_path == '':
            return

        try:
            projects.CreateProject(video_file_path)
            projects.GetRecentProjects().AddRecentProject(projects.GetCurrentProject().project_path)
            self.NotifyObservers()
        except Exception as e:
            print(f"Failed to create project: {e}")
            return

    def LoadProject(self, project_path):
        if project_path == '':
            return

        projects.LoadProject(project_path)
        projects.GetRecentProjects().AddRecentProject(projects.GetCurrentProject().project_path)
        self.NotifyObservers()

def GetProjectService() -> ProjectService:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = ProjectService()
    return _SINGLETON
