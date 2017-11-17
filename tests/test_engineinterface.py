from sftoolbox.engineinterface import Engine
from sftoolbox.actions import Action
from sftoolbox.content import Content


class TestAction(Action):
    """test action
    """


class TestContent(Content):
    """test content
    """


def test_engine_register_action():
    engine = Engine()
    assert engine
    engine.register_action_class(TestAction)
    assert engine.action_classes_register == [TestAction]


def test_engine_register_content():
    engine = Engine()
    assert engine
    engine.register_content_class(TestContent)
    assert engine.content_classes_register == [TestContent]
