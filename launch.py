"""launch toolbox
"""
import sys
import argparse

from sftoolboxqt import qtgui
from sftoolbox.projects import Project
from sftoolboxqt.widgets import ProjectWidget


def main(args):
    """launch sf toolbox
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')
    parser.add_argument('--live', action='store_true', default=False)
    app = qtgui.QApplication([])

    namespace = parser.parse_args(args)
    project = None
    if namespace.project:
        project = Project(namespace.project)

    w = ProjectWidget(project)
    w.live_edit = namespace.live

    w.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
