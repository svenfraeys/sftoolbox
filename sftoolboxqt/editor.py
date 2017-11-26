"""gui systems to manage actions
"""
import os

from sftoolbox.content import ActionContent, PanelContent
from sftoolboxqt import qtgui, qtcore
from sftoolboxqt.tree import PanelsModel, PanelsTreeWidget


class ActionsTreeWidget(qtgui.QTreeWidget):
    """tree widget holding actions
    """

    def startDrag(self, dropAction):
        # create mime data object
        mime = qtcore.QMimeData()
        mime.setData('application/x-item', '???')
        # start drag
        drag = qtgui.QDrag(self)
        drag.setMimeData(mime)
        # drag.start(qtcore.Qt.CopyAction)
        # drag.start(qtcore.Qt.CopyAction)
        drag.exec_(dropAction, qtcore.Qt.MoveAction)


class PanelsWidget(qtgui.QWidget):
    """browser for panels
    """

    def __init__(self, project=None, parent=None):
        """construct the browser
        """
        super(PanelsWidget, self).__init__(parent=parent)
        self.setWindowTitle('Panels Browser')
        self._project = project
        self._tree_model = PanelsModel(project)
        self._tree = self._create_panels_tree_widget(self._tree_model)

        layout = qtgui.QVBoxLayout()
        layout.addWidget(self._tree)

        self.setLayout(layout)

    def _create_panels_tree_widget(self, model):
        """return tree widget that will contain the actions
        """
        tree = PanelsTreeWidget()
        tree.setModel(model)
        tree.setSortingEnabled(True)
        tree.setDragEnabled(True)
        tree.setAcceptDrops(True)
        return tree

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._tree_model.project = value


class ActionsWidget(qtgui.QWidget):
    """browser system for browsing trough the actions
    """

    def _create_actions_tree_widget(self):
        """return tree widget that will contain the actions
        """
        tree = ActionsTreeWidget()
        tree.setHeaderLabels(['Action', 'IDName', 'Tags'])
        tree.setSortingEnabled(True)
        tree.setDragEnabled(True)
        return tree

    def __init__(self, project=None, parent=None):
        """construct the browser
        """
        super(ActionsWidget, self).__init__(parent=parent)
        self.setWindowTitle('Actions Browser')
        self._project = project
        self._tree_widget = self._create_actions_tree_widget()

        layout = qtgui.QVBoxLayout()
        layout.addWidget(self._tree_widget)

        self.setLayout(layout)
        layout.addWidget(self._tree_widget)
        self._refresh_content()

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._refresh_content()

    def _handle_item_double_clicked(self, item):
        """handle doubleclicking item
        """
        item.action.run()

    def _refresh_content(self):
        """refresh the content
        """
        self._tree_widget.clear()
        self._tree_widget.itemDoubleClicked.connect(
            self._handle_item_double_clicked)
        if not self.project:
            return

        for action in self.project.actions:
            item = qtgui.QTreeWidgetItem()
            icon_filepath = action.absolute_icon_filepath
            if icon_filepath and os.path.exists(icon_filepath):
                item.setIcon(0, qtgui.QIcon(icon_filepath))

            item.setText(0, action.human_label)
            item.setText(1, action.idname)
            item.setText(2, ', '.join(map(str, action.tags)))
            item.action = action
            self._tree_widget.addTopLevelItem(item)


class EditorWidget(qtgui.QWidget):
    """"""

    def __init__(self, project=None, parent=None):
        """construct the browser
        """
        super(EditorWidget, self).__init__(parent=parent)
        self.setWindowTitle('Editor')

        self._actions_widget = ActionsWidget(project)
        self._panels_widget = PanelsWidget(project)

        layout = qtgui.QHBoxLayout()

        splitter = qtgui.QSplitter(qtcore.Qt.Horizontal)
        splitter.addWidget(self._panels_widget)
        splitter.addWidget(self._actions_widget)
        layout.addWidget(splitter)
        self.setLayout(layout)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._actions_widget.project = value
        self._panels_widget.project = value

    def sizeHint(self):
        return qtcore.QSize(900, 800)
