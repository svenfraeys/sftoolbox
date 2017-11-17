import pytest

import sftoolbox
from sftoolbox.actions import Action, PythonCodeAction, action_from_json
from sftoolbox.projects import Project


def test_action():
    project = Project()

    assert Action
    action = Action(project)
    assert action


def test_action_from_json():
    project = Project()
    action_json = {'idname': 'hello'}
    action = Action.from_json(project, action_json)
    assert action.idname == 'hello'


def test_action_run():
    project = Project()
    action = Action(project)
    assert action.run() is True


def test_python_code_action():
    project = Project()
    assert PythonCodeAction(project)
    code = 'assert True'
    data = {
        'idname': 'yes',
        'code': code
    }
    action = PythonCodeAction.from_json(project, data)
    assert action.code == code
    assert action.is_runnable
    assert action.run()

    action.code = ''
    assert not action.is_runnable


@sftoolbox.engine.register_action_class
class FailRunAction(Action):
    """action that always returns false
    """
    json_type = 'test_fail_run'

    def run(self):
        return False


def test_fail_run_action():
    """test the action that got registered above and see that we can make it
    """
    project = Project()
    action = action_from_json(project, {'type': 'test_fail_run'})
    assert isinstance(action, FailRunAction)
    assert action.run() is False
