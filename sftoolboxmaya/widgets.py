import sftoolboxmaya.utils
from sftoolboxqt import qtgui
from sftoolboxqt.widgets import ProjectWidget


class MayaProjectWidget(sftoolboxmaya.utils.DialogWidget):
    """toolbox widget
    """

    def _wrapped_set_window_title(self, func):
        """wrap for the set window title to keep it synced
        """

        def wrapped_func(text):
            self.setWindowTitle(text)
            func(text)

        return wrapped_func

    def __init__(self, project=None, parent=None):
        """settings and context are given for the init
        """
        super(MayaProjectWidget, self).__init__()
        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._toolbox_widget = ProjectWidget(project)
        self.setWindowTitle(self._toolbox_widget.windowTitle())

        # wrap the set window title so we keep it in sync
        self._toolbox_widget.setWindowTitle = self._wrapped_set_window_title(
            self._toolbox_widget.setWindowTitle)

    @property
    def project(self):
        return self._toolbox_widget.project

    @project.setter
    def project(self, value):
        self._toolbox_widget.project = value

    @property
    def active_panel(self):
        return self._toolbox_widget.active_panel

    @active_panel.setter
    def active_panel(self, value):
        self._toolbox_widget.active_panel = value
