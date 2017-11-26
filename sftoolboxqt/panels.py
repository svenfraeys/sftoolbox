"""panels widget
"""
from sftoolboxqt import qtgui


class PanelsWidget(qtgui.QWidget):
    """panels widget
    """

    def __init__(self, project, parent=None):
        super(PanelsWidget, self).__init__(parent=parent)
        self._project = project
        self._tree = qtgui.QTreeWidget()

        layout = qtgui.QVBoxLayout()
        layout.addWidget(self._tree)
        self.setLayout(layout)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._refresh_content()

    def _refresh_content(self):
        """refresh the gui
        """
        for panel in self.project.panels:
            pass
