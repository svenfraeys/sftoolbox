import sftoolbox


class Variable(object):
    """variable
    """

    def __init__(self, project):
        """construct"""
        project.add(self)
        self.project = project
        self.idname = None

    def _apply_json(self, data):
        """apply the json data
        """
        self.label = data.get('label')
        self.idname = data.get('idname')

    @classmethod
    def from_json(cls, project, value):
        instance = cls(project)
        instance._apply_json(value)
        return instance


@sftoolbox.engine.register_variable_class
class TextVariable(Variable):
    """text
    """
    json_type = 'text'

    def __init__(self, project):
        super(TextVariable, self).__init__(project)
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def _apply_json(self, data):
        super(TextVariable, self)._apply_json(data)


def from_json(project, value):
    """return a action from the given json
    """
    json_type = value.get('type')
    for class_ in sftoolbox.engine.variable_classes_register:
        if json_type == class_.json_type:
            return class_.from_json(project, value)

    return Variable.from_json(project, value)
