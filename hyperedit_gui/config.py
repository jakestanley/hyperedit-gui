from common_py.config import Config
from hyperedit_gui.projects import RecentProjects

class HeConfig(Config):
    def __init__(self) -> None:
        super().__init__('hyperedit_gui')
        self.projects = RecentProjects(self.config["projects"])

    def _PrepareSave(self):
        return dict(
            projects=self.projects.projects
        )

    def _DefaultConfig(self):
        return dict(
            projects=[]
        )
