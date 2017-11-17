from sftoolbox.projects import Project
from sftoolbox.content import Content, ActionContent, PanelContent


def test_content():
    project = Project()
    content = Content(project)
    assert content


def test_action_content():
    project = Project()
    assert ActionContent(project, 'hello')


def test_panel_content():
    project = Project()
    assert PanelContent(project, 'hello')
