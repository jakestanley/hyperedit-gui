import hyperedit_gui.model.projects as projects
from hyperedit_gui.model.recent_projects import GetRecentProjects
from hyperedit_gui.view.files import FindProjectFile, FindVideoFile
from hyperedit_gui.model.config import GetConfig
from hyperedit_gui.service.observable_service import ObservableService

_SINGLETON = None

class ProjectService(ObservableService):
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("ProjectService MUST only be instantiated once")
        super().__init__()

    def NotifyObserver(self, observer):
        observer.OnProjectChange()

    def PostConstruct(self):
        pass

    def CreateProject(self, video_file_path):
        
        if video_file_path == '':
            return

        try:
            projects.CreateProject(video_file_path)
            GetRecentProjects().AddRecentProject(projects.GetCurrentProject().project_path) 
            GetConfig().Save()
            self.NotifyObservers()
        except Exception as e:
            print(f"Failed to create project: {e}")
            return
    
    def LoadProject(self, project_path):
        if project_path == '':
            return

        projects.LoadProject(project_path)
        GetRecentProjects().AddRecentProject(projects.GetCurrentProject().project_path)
        # LoadSrts(self.GetSrtFilePath())
        # self.SetDeaggressSeconds(GetCurrentProject().deaggress_seconds)
        self.NotifyObservers()
    
    def remove_project(self, project_path):
        GetRecentProjects().RemoveRecentProject(project_path)
        GetConfig().Save()

    def locate_files(self, project: projects.Project):
        old_project_path = project.project_path
        if not project.IsProjectPathValid():
            project.project_path = FindProjectFile(project.name)
            project = projects.GlanceProject(project.project_path)
        if not project.IsVideoPathValid():
            project.video_path = FindVideoFile(project.video_path)
        project.Save()
        GetRecentProjects().ReplaceRecentProject(old_project_path, project.project_path)
    
def GetProjectService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = ProjectService()
    return _SINGLETON
