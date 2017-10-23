import sftoolbox.actions


def test_basic_action():
    a = sftoolbox.actions.Action()
    assert a


def test_python_code_action():
    a = sftoolbox.actions.PythonCodeAction(code="print hello world")
    a.run()
