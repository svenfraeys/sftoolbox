import shiboken2
from maya import OpenMayaUI as mui
from toolboxqt import qtgui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def get_maya_main_window():
    """return the main window of maya

    :rtype: QtWidgets.QMainWindow
    """
    ptr = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(ptr), qtgui.QMainWindow)


class DialogWidget(MayaQWidgetDockableMixin, qtgui.QDialog):
    """base dialog widget setup for maya to inherit from or use
    """

    def __init__(self, parent=None):
        super(DialogWidget, self).__init__(parent=parent)
