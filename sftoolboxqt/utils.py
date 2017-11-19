from sftoolboxqt import qtgui
from sftoolboxqt import qtcore
import os
import sys


def open_with_default_program(filepath):
    """open the given filepath with default system software
    """
    if hasattr(qtgui, "QDesktopServices"):
        qtgui.QDesktopServices.openUrl(qtcore.QUrl(filepath))
    elif sys.platform == 'win32':
        os.system("start " + filepath)
    elif sys.platform == 'posix':
        os.system('open "{0}"'.format(filepath))
    elif sys.platform in ['linux', 'linux2']:
        os.system('xdg-open "{0}"'.format(filepath))


def get_icon_size(wanted_size):
    """return the qsize needed for the given size
    """
    if wanted_size == 'large':
        return qtcore.QSize(32, 32)
    elif wanted_size == 'medium':
        return qtcore.QSize(25, 25)
    elif wanted_size == 'huge':
        return qtcore.QSize(50, 50)
    else:
        return qtcore.QSize(16, 16)
