import os
import sys
from sftoolbox.actions import Action
import sftoolbox
import MaxPlus


@sftoolbox.engine.register_action_class
class MaxScriptEvalAction(Action):
    """mel eval
    """
    json_type = 'max_code'

    def __init__(self, project, code=None):
        """construct the project
        """
        super(MaxScriptEvalAction, self).__init__(project)
        self.code = code

    def _apply_json(self, data):
        super(MaxScriptEvalAction, self)._apply_json(data)
        self.code = data.get('code', None)

    @classmethod
    def from_json(cls, project, data):
        """return instance made from given json
        """
        action = cls(project)
        action._apply_json(data)
        return action

    def run(self):
        MaxPlus.Core.EvalMAXScript(self.code)


@sftoolbox.engine.register_action_class
class MaxScriptAction(Action):
    """run a python script filepath that is given
    """
    json_type = 'max_script'

    def __init__(self, project, filepath=None):
        """python script filepath
        """
        super(MaxScriptAction, self).__init__(project)
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

    def _apply_json(self, data):
        super(MaxScriptAction, self)._apply_json(data)
        self.filepath = data.get('filepath', None)

    @classmethod
    def from_json(cls, project, data):
        """return instance made from given json
        """
        action = cls(project)
        action._apply_json(data)
        return action