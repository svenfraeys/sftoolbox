from sftoolbox.content import PanelContent, ActionContent
from sftoolboxqt import qtcore, qtgui
import uuid


class Node(object):
    """base node
    """

    def __init__(self):
        """"""
        self.guid = str(uuid.uuid4())

    @property
    def parent(self):
        raise NotImplemented

    @property
    def children(self):
        raise NotImplemented

    @property
    def row(self):
        raise NotImplemented

    @property
    def human_label(self):
        raise NotImplemented

    @property
    def type(self):
        raise NotImplemented

    def find_by_guid(self, guid):
        if self.guid == guid:
            return self

        for child in self.children:
            child_result = child.find_by_guid(guid)
            if child_result:
                return child_result

        return None

    def add_child(self, child):
        return

    def remove_child(self, child):
        return


class ContentNode(Node):
    """content node for tree
    """

    def __init__(self, content, parent, row):
        super(ContentNode, self).__init__()
        self.content = content
        self._parent = parent
        self._row = row
        self._children = None

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        if self._children is not None:
            return self._children

        children = []
        if isinstance(self.content, PanelContent):
            for i, content in enumerate(self.content.target_panel.content):
                children.append(ContentNode(content, self, i))
        self._children = children
        return children

    @property
    def human_label(self):
        if isinstance(self.content, PanelContent):
            return self.content.target_panel.human_label
        elif isinstance(self.content, ActionContent):
            return self.content.target_action.human_label

    @property
    def row(self):
        return self._row

    @property
    def type(self):
        if isinstance(self.content, PanelContent):
            return 'Panel'
        elif isinstance(self.content, ActionContent):
            return 'Action'

    def add_child(self, child):
        if isinstance(self.content, PanelContent):
            panel = self.content.panel
            if isinstance(child, ContentNode):
                child.content.target_panel = panel

        return

    def remove_child(self, child):
        """remove the child
        """


class PanelNode(Node):
    """panel node for tree
    """

    def __init__(self, panel, parent, row):
        super(PanelNode, self).__init__()
        self._panel = panel
        self._parent = parent
        self._row = row
        self._children = None

    @property
    def row(self):
        return self._row

    @property
    def parent(self):
        return self._parent

    @property
    def human_label(self):
        return self._panel.human_label

    @property
    def children(self):
        if self._children is not None:
            return self._children

        children = []

        if not self._panel:
            return []

        for i, content in enumerate(self._panel.content):
            content_node = ContentNode(content, self, i)
            children.append(content_node)
        self._children = children

        return children

    @property
    def type(self):
        return 'Panel'


class ProjectNode(Node):
    """return project node
    """

    def __init__(self, project):
        super(ProjectNode, self).__init__()
        self._project = project
        self._children = None

    @property
    def children(self):
        """return list of child nodes
        """
        if not self._project:
            return []

        if self._children is not None:
            return self._children

        children = []

        for i, panel in enumerate(self._project.panels):
            panel_node = PanelNode(panel, self, i)
            children.append(panel_node)
        self._children = children
        return children

    @property
    def parent(self):
        return None

    @property
    def row(self):
        return 0

    @property
    def type(self):
        return 'Project'


class PanelsModel(qtcore.QAbstractItemModel):
    """model for the panels
    """

    def __init__(self, project=None, parent=None):
        super(PanelsModel, self).__init__(parent=parent)
        self._project = project
        self._project_node = ProjectNode(project)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self._project_node = ProjectNode(value)

    def columnCount(self, parent):
        """return column count
        """
        return 2

    def rowCount(self, parent):
        """total rows
        """
        if not parent.isValid():
            return len(self._project_node.children)

        node = parent.internalPointer()
        if not node:
            return 0

        return len(node.children)

    def parent(self, index):
        """return the parent
        """
        # no parent
        if not index.isValid():
            return qtcore.QModelIndex()

        node = index.internalPointer()
        if not node or not node.parent:
            return qtcore.QModelIndex()

        return self.createIndex(node.parent.row, 0, node.parent)

    def index(self, row, column, parent):
        """return the model index
        """
        if not parent.isValid():
            if row >= len(self._project_node.children):
                return qtcore.QModelIndex()

            node = self._project_node.children[row]
            index = self.createIndex(row, column, node)
            return index

        node = parent.internalPointer()
        if row >= len(node.children):
            return qtcore.QModelIndex()

        child_node = node.children[row]
        index = self.createIndex(row, column, child_node)

        return index

    def data(self, index, role):
        """return the data
        """
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == qtcore.Qt.DisplayRole:
            if index.column() == 0:
                return node.human_label
            elif index.column() == 1:
                return node.type

        elif role == qtcore.Qt.DisplayRole and index.column() == 1:
            return ''
        elif role == qtcore.Qt.ToolTipRole:
            return 'Tooltip'
        elif role != qtcore.Qt.DisplayRole:
            return None

    def headerData(self, section, orientation, role):
        if orientation == qtcore.Qt.Horizontal and \
                        role == qtcore.Qt.DisplayRole and section == 0:
            return 'Name'
        return None

    def supportedDropActions(self):
        """which drops do we support
        """
        return qtcore.Qt.CopyAction | qtcore.Qt.MoveAction

    def flags(self, index):
        """default flags
        """
        default_flags = super(PanelsModel, self).flags(index)

        if index.isValid():
            return qtcore.Qt.ItemIsDragEnabled | \
                   qtcore.Qt.ItemIsDropEnabled | default_flags
        else:
            return qtcore.Qt.ItemIsDropEnabled | default_flags

    def dropMimeData(self, data, action, row, column, parent):
        """handle drop mime data
        """
        if data.hasFormat('application/x-tree-node'):
            guids = str(data.data('application/x-tree-node')).split(',')
            nodes = []

            for guid in guids:
                node = self._project_node.find_by_guid(guid)
                if not node:
                    raise RuntimeError(
                        'could not find node with guid {0}'.format(guid))
                nodes.append(node)

            if parent.isValid():
                parent_node = parent.internalPointer()
                for node in nodes:
                    if node.parent:
                        node.parent.remove_child(node)

                    parent_node.add_child(node)

        return True

    def canDropMimeData(self, data, action, row, column, parent):
        """check if it can drop
        """
        return True

    def mimeData(self, indexes):
        """return mime data for the given indexes
        """
        guids = []
        for index in indexes:
            if not index.isValid():
                continue
            node = index.internalPointer()
            guids.append(node.guid)

        mime_data = qtcore.QMimeData()
        mime_data.setData('application/x-tree-node', ','.join(guids))
        return mime_data

    def mimeTypes(self):
        return ['text/plain', 'application/x-action',
                'application/x-tree-node']


class PanelsTreeWidget(qtgui.QTreeView):
    """tree widget to manage panels
    """

    def __init__(self, parent=None):
        super(PanelsTreeWidget, self).__init__(parent=parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
