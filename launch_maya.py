"""launch toolbox
"""
import os
import sys
import inspect
import argparse

# modules that need to be popped
modules = ['sftoolbox', 'sftoolboxmaya']
sftoolbox_widgets = []


def main(args=None):
    """launch the tool for maya
    """
    if not args:
        args = []

    # pop all modules from cache for latest code
    map(sys.modules.pop, [key for key in sys.modules.keys()
                          if any([mod in key for mod in modules])])

    # make toolbox modules available for import
    current_python_file = inspect.getfile(inspect.currentframe())
    module_root = os.path.dirname(current_python_file)

    if module_root in sys.path:
        sys.path.remove(module_root)

    sys.path.insert(0, module_root)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')

    namespace = parser.parse_args(args)
    project = None

    from sftoolbox.project import Project
    from sftoolboxmaya.widgets import MayaProjectWidget
    from sftoolboxmaya import actions
    assert actions

    if namespace.project:
        project = Project(namespace.project)

    w = MayaProjectWidget(project)
    sftoolbox_widgets.append(w)
    w.show(dockable=True)


if __name__ == '__main__':
    main([])
