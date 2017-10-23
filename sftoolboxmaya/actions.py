from sftoolbox.actions import Action
import sftoolbox
from maya import mel


@sftoolbox.engine.register_action_class
class MelEvalAction(Action):
    """mel eval
    """
    json_type = 'mel_eval'

    def __init__(self, project, code=None):
        """construct the project
        """
        super(MelEvalAction, self).__init__(project)
        self.code = code

    def _apply_json(self, data):
        super(MelEvalAction, self)._apply_json(data)
        self.code = data.get('code', None)

    @classmethod
    def from_json(cls, project, data):
        """return instance made from given json
        """
        action = cls(project)
        action._apply_json(data)
        return action

    def run(self):
        mel.eval(self.code)
