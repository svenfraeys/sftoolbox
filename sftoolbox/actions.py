"""actions to use
"""
import sftoolbox.utils
import os
import sys
import uuid

import imp

import sftoolbox


class Action(object):
    """base implmentation of an action
    """
    json_type = 'action'

    def __init__(self, project):
        """construct the action
        """
        project.add(self)
        self.project = project
        self.label = None
        self.idname = str(uuid.uuid4())
        self.description = None
        self.icon_filepath = None
        self.enabled = True
        self.visible = True
        self.style_sheet = None

    def _apply_json(self, data):
        """apply the json data
        """
        self.label = data.get('label')
        self.idname = data.get('idname')
        self.description = data.get('description')
        self.icon_filepath = data.get('icon')
        self.enabled = data.get('enabled', True)
        self.visible = data.get('visible', True)
        self.style_sheet = data.get('style_sheet', None)

    @property
    def absolute_icon_filepath(self):
        if self.icon_filepath:
            return os.path.join(self.project.directory, self.icon_filepath)
        return None

    @classmethod
    def from_json(cls, project, data):
        action = cls(project)
        action._apply_json(data)
        return action

    def run(self):
        """run the given action
        """
        return True

    @property
    def is_runnable(self):
        return True

    @property
    def human_label(self):
        if self.label:
            return str(self.label)
        else:
            return sftoolbox.utils.human_readable(str(self.idname))


@sftoolbox.engine.register_action_class
class DummyAction(Action):
    """dummy action not doing anything
    """
    json_type = 'dummy'

    def run(self):
        """run the dummy action doing nothing
        """
        return True


@sftoolbox.engine.register_action_class
class PythonCodeAction(Action):
    """python string execution
    """
    json_type = 'python'

    def __init__(self, project, code=None):
        super(PythonCodeAction, self).__init__(project)
        self.code = code

    def _apply_json(self, data):
        super(PythonCodeAction, self)._apply_json(data)
        self.code = data.get('code', None)

    @property
    def is_runnable(self):
        if not self.code:
            return False
        return True

    def run(self):
        if self.code:
            exec (self.code)
            return True
        else:
            raise False


@sftoolbox.engine.register_action_class
class PythonScriptAction(Action):
    """run a python script filepath that is given
    """
    json_type = 'python_script'

    def __init__(self, project, filepath=None):
        """python script filepath
        """
        super(PythonScriptAction, self).__init__(project)
        self.filepath = filepath

    @property
    def absolute_filepath(self):
        filepath = os.path.join(self.project.directory, self.filepath)
        return filepath

    @property
    def is_runnable(self):
        if not os.path.exists(self.absolute_filepath):
            return False
        return True

    def run(self):
        if sys.version_info > (3, 0):
            exec (open(self.absolute_filepath).read())
        else:
            execfile(self.absolute_filepath)
        return True

    def _apply_json(self, data):
        super(PythonScriptAction, self)._apply_json(data)
        self.filepath = data.get('filepath', None)


@sftoolbox.engine.register_action_class
class PythonFunctionAction(Action):
    """run a python script filepath that is given
    """
    json_type = 'python_function'

    def __init__(self, project, filepath=None):
        """python script filepath
        """
        super(PythonFunctionAction, self).__init__(project)
        self.filepath = filepath
        self.function_name = None
        self.args = []
        self.kwargs = {}

    @property
    def absolute_filepath(self):
        if not self.filepath:
            return

        return os.path.join(self.project.directory, self.filepath)

    @property
    def is_runnable(self):

        if not self.absolute_filepath:
            return False

        if not os.path.exists(self.absolute_filepath):
            return False
        return True

    def run(self):
        """load the module and run the function
        """

        module_name = os.path.basename(self.absolute_filepath)
        module_name, _ = os.path.splitext(module_name)
        module_object = imp.load_source(module_name, self.absolute_filepath)
        function_name = self.function_name

        if not function_name:
            function_name = 'main'

        func = getattr(module_object, function_name)
        func(*self.args, **self.kwargs)
        return True

    def _apply_json(self, data):
        super(PythonFunctionAction, self)._apply_json(data)
        self.filepath = data.get('filepath', None)
        self.function_name = data.get('function', None)
        self.args = data.get('args', [])
        self.kwargs = data.get('kwargs', {})


def action_from_json(project, value):
    """return a action from the given json
    """
    json_type = value.get('type')
    for class_ in sftoolbox.engine.action_classes_register:
        if json_type == class_.json_type:
            return class_.from_json(project, value)

    return DummyAction.from_json(project, value)
