"""launch toolbox
"""
import sys
import argparse

from sftoolboxqt import qtgui
from sftoolbox.projects import load_project_from_filepath
from sftoolboxqt.widgets import ProjectWidget


def main(args=None):
    """launch sf toolbox
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')
    parser.add_argument('--live', action='store_true', default=False)
    app = qtgui.QApplication([])

    namespace = parser.parse_args(args)
    project = None
    if namespace.project:
        project = load_project_from_filepath(namespace.project)

    w = ProjectWidget(project)
    w.live_edit = namespace.live

    w.show()

    app.exec_()
    sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
