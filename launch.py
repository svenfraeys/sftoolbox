"""launch toolbox
"""
import argparse

import sys

from sftoolboxqt import qtgui
from sftoolbox.project import Project
from sftoolboxqt.widgets import ProjectWidget


def main(args):
    """launch sf toolbox
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')
    parser.add_argument('--live')
    app = qtgui.QApplication([])

    namespace = parser.parse_args(args)
    project = None
    if namespace.project:
        project = Project(namespace.project)

    w = ProjectWidget(project)
    w.live_edit = True

    w.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
