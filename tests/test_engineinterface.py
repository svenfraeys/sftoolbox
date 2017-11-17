from sftoolbox.engineinterface import Engine
from sftoolbox.actions import Action
from sftoolbox.content import Content


class _Action(Action):
    """test action
    """


class _Content(Content):
    """test content
    """


def test_engine_register_action():
    engine = Engine()
    assert engine
    engine.register_action_class(_Action)
    assert engine.action_classes_register == [_Action]


def test_engine_register_content():
    engine = Engine()
    assert engine
    engine.register_content_class(_Content)
    assert engine.content_classes_register == [_Content]
