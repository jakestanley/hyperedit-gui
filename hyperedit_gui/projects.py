import json
from typing import List

_MAX_PROJECTS = 10

class Project:
    def __init__(self, name, path) -> None:
        self.name = name
        self.path = path

class RecentProjects:
    def __init__(self, projects=[]):
        self.projects = projects

    def add_project(self, project):
        if project in self.projects:
            self.touch_project(project)
        else:
            self.projects.append(project)
        if len(self.projects) > _MAX_PROJECTS:
            self.projects.pop(0)

    def touch_project(self, project):
        self.projects.remove(project)
        self.projects.append(project)

    def remove_project(self, project):
        self.projects.remove(project)

    def read_projects(self):
        return [ 
            ReadProject(project) for project in self.projects
        ]

def ReadProject(project_path) -> Project:
    try:
        with open(project_path, 'r') as project_file:
            project = json.load(project_file)
            return Project(project.get('name', "<NO NAME>"), project_path)
    except json.decoder.JSONDecodeError:
        return Project("<INVALID JSON>", project_path)
    except FileNotFoundError:
        return Project("<MISSING>", project_path)

