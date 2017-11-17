from sftoolbox.utils import human_readable


def test_human_readable():
    assert human_readable('hello') == 'Hello'
    assert human_readable('hello.world') == 'Hello World'
    assert human_readable('hello_world') == 'Hello World'
