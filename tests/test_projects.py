import unittest

from hyperedit_gui.projects import RecentProjects

class RecentProjectsTest(unittest.TestCase):

    def test_add_project_limit(self):
        recent_projects = RecentProjects()
        for i in range(0, 10):
            recent_projects.add_project(f'test_project_{i}')
        self.assertEqual(len(recent_projects.projects), 10)

        # add another project, and the first project should be removed
        recent_projects.add_project('test_project_10')
        self.assertNotIn('test_project_0', recent_projects.projects)

    def test_add_project(self):
        recent_projects = RecentProjects()
        recent_projects.add_project('test_project')
        self.assertEqual(recent_projects.projects, ['test_project'])

    def test_add_existing_project(self):
        recent_projects = RecentProjects()
        recent_projects.add_project('test_project')
        recent_projects.add_project('test_project')
        self.assertEqual(recent_projects.projects, ['test_project'])

    def test_load_projects(self):
        projects = ['test_project_1', 'test_project_2']
        recent_projects = RecentProjects(projects)
        self.assertEqual(recent_projects.projects, projects)

if __name__ == '__main__':
    unittest.main()
