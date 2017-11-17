from sftoolbox.panels import Panel
from sftoolbox.projects import Project


def test_panel():
    project = Project()
    panel = Panel(project)
    assert panel
