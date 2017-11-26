"""widgets available for toolbox
"""
import os
from sftoolbox.content import ActionContent
import sftoolbox
import sftoolbox.content
from sftoolbox.projects import load_project_from_filepath
from sftoolboxqt import qtgui
from sftoolboxqt.editor import EditorWidget
from sftoolboxqt import utils
from sftoolboxqt import qtcore
from sftoolboxqt.styles import create_style
import sftoolbox.utils


class ReloadProjectThread(qtcore.QThread):
    """reload live project
    """
    project_changed = qtcore.Signal(str)

    def __init__(self):
        super(ReloadProjectThread, self).__init__()
        self.filepath = None
        self.previous_hash = None

    def run(self):
        import time

        while True:
            time.sleep(1)
            filepath = self.filepath
            if filepath and os.path.exists(filepath):
                current_hash = sftoolbox.utils.get_hash_from_file(filepath)
                if self.previous_hash != current_hash:
                    self.previous_hash = current_hash
                    self.project_changed.emit(filepath)


class ActionWidget(qtgui.QWidget):
    """action button
    """

    def __init__(self, action=None, show_text=True, show_icons=True,
                 icon_size=None, parent=None):
        super(ActionWidget, self).__init__(parent=parent)
        self.action = action
        self._button = qtgui.QPushButton()
        self.show_text = show_text
        self.show_icons = show_icons
        self.icon_size = icon_size

        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        layout.addWidget(self._button)
        self._refresh_content()

    @property
    def label(self):
        if self.action:
            return self.action.human_label
        else:
            return 'Empty'

    def _refresh_content(self):
        """refresh the content
        """
        self.setWindowTitle(self.label)
        if self.show_text:
            self._button.setText(self.label)
        else:
            self._button.setText('')

        if self.action:

            self.setWindowTitle(self.action.human_label)
            self._button.setToolTip(self.action.description)
            self._button.setStatusTip(self.action.description)
            self._button.clicked.connect(self._handle_click)
            self._button.setEnabled(self.action.enabled)
            self._button.setVisible(self.action.visible)
            self._button.setStyleSheet(self.action.style_sheet or '')

            icon_filepath = self.action.absolute_icon_filepath
            if self.show_icons:
                if icon_filepath and os.path.exists(icon_filepath):
                    self._button.setIcon(qtgui.QIcon(icon_filepath))
                    self._button.setIconSize(
                        utils.get_icon_size(self.icon_size))

    def _handle_click(self):
        """handle clicking on the action button
        """
        if not self.action.is_runnable:
            print('can not run this action...')
            return

        self.action.run()


class ContentWidget(qtgui.QWidget):
    """content button
    """

    def __init__(self, content=None, show_icons=True, show_text=True,
                 icon_size=None,
                 parent=None):
        """construct the button
        """
        super(ContentWidget, self).__init__(parent=parent)
        self.content = content
        self.show_text = show_text
        self.show_icons = show_icons
        self.icon_size = icon_size

        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._refresh_content()

    def _refresh_content(self):
        """content
        """
        if not self.content:
            return

        if isinstance(self.content, sftoolbox.content.ActionContent):
            widget = ActionWidget(self.content.target_action,
                                  show_icons=self.show_icons,
                                  show_text=self.show_text,
                                  icon_size=self.icon_size)

        elif isinstance(self.content, sftoolbox.content.PanelContent):
            widget = PanelWidget(self.content.target_panel)
        else:
            raise
        layout = self.layout()
        layout.addWidget(widget)


class PanelWidget(qtgui.QWidget):
    """panel widget
    """

    def __init__(self, panel=None, parent=None):
        super(PanelWidget, self).__init__(parent=parent)
        self.panel = panel
        self.setAcceptDrops(True)

        self.style = create_style(panel.style, panel)

        layout = qtgui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.style)

        self.setLayout(layout)
        self._refresh_content()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def add_content(self, content, show_icons=True, show_text=True):
        """add content
        """
        return

    def dropEvent(self, event):
        source = event.source()
        if isinstance(source, qtgui.QTreeWidget):
            for item in source.selectedItems():
                content = ActionContent(self.panel.project, item.action.idname)
                content.panel = self.panel
            self._refresh_content()

        event.acceptProposedAction()

    def _refresh_content(self):
        """refresh the content of the panel
        """
        if self.panel:
            self.setWindowTitle(self.panel.human_label)
            self.setToolTip(self.panel.description)
            self.setStatusTip(self.panel.description)
            self.setStyleSheet(self.panel.style_sheet or '')

            self.style.clear_content()

            for content in self.panel.content:
                self.style.add_content(content,
                                       show_icons=self.panel.show_icons,
                                       show_text=self.panel.show_text)


class MainPanelWidget(PanelWidget):
    """panel widget that is going to be the one floating around
    """

    def _refresh_content(self):
        """refreshing of this widget is a bit different
        """
        super(MainPanelWidget, self)._refresh_content()
        layout = self.layout()
        spacer = qtgui.QSpacerItem(0, 0, qtgui.QSizePolicy.Minimum,
                                   qtgui.QSizePolicy.MinimumExpanding)
        layout.addItem(spacer)


class ProjectWidget(qtgui.QWidget):
    """toolbox main window
    """
    _instances = []

    def _make_scroll_area(self):
        """return the scroll area
        """
        scroll_area = qtgui.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(qtgui.QFrame.NoFrame)
        return scroll_area

    def _create_edit_project(self):
        """return action to edit the project
        """
        action = qtgui.QAction(self)
        action.setText('Edit Project...')
        action.triggered.connect(self._handle_edit_project)
        return action

    def _handle_edit_project(self):
        """edit the project
        """
        if not self.project:
            print('no current project')
            return

        if not self.live_edit:
            answer = qtgui.QMessageBox.question(
                self, "Activate Live Edit ?",
                "Do you want to enable live edit "
                "so changes are live updated ?",
                qtgui.QMessageBox.Yes | qtgui.QMessageBox.No)

            if answer == qtgui.QMessageBox.Yes:
                self.live_edit = True

        utils.open_with_default_program(self.project.filepath)

    def _create_open_project_action(self):
        """open project
        """
        action = qtgui.QAction(self)
        action.setText('Open Project...')
        action.triggered.connect(self._handle_open_project)
        return action

    def _create_close_project_action(self):
        """open project
        """
        action = qtgui.QAction(self)
        action.setText('Close Project')
        action.triggered.connect(self._handle_close_project)
        return action

    def _handle_close_project(self):
        """close the current project
        """
        if self.project:
            self.project = None

    def _handle_open_project(self):
        """open a project
        """
        filepath, _ = qtgui.QFileDialog.getOpenFileName(
            self, "Select Toolbox yaml file",
            filter="yaml (*.yaml);;All Files (*.*)"
        )

        if not filepath:
            return

        project = load_project_from_filepath(filepath)
        self.project = project

    def _create_about_action(self):
        """return action that shows the about of the tool
        """
        action = qtgui.QAction(self)
        action.setText('About')
        action.triggered.connect(self._show_about)
        return action

    def _create_about_toolbox_action(self):
        """return action that shows the about information from tool box
        """
        action = qtgui.QAction(self)
        action.setText('About SF Tool Box')
        action.triggered.connect(self._show_about_tool_box)
        return action

    def _create_reload_action(self):
        """return a action that triggers a reload
        """
        action = qtgui.QAction(self)
        action.setText('Reload Project')
        action.triggered.connect(self._handle_reload)
        return action

    def _handle_reload(self):
        """handle reload
        """
        self._refresh_content()

    def _create_close_action(self):
        """create a close action
        """
        action = qtgui.QAction(self)
        action.setText("Close")
        action.triggered.connect(self.close)
        return action

    def _create_live_edit_action(self):
        """create a close action
        """
        action = qtgui.QAction(self)
        action.setText("Live Edit")
        action.triggered.connect(self._handle_live_edit)
        action.setCheckable(True)
        return action

    def _handle_live_edit(self):
        """handle toggle of live edit
        """
        self.live_edit = not self.live_edit

    def _show_about_tool_box(self):
        """show about toolbox
        """
        title = 'SF ToolBox - {0}'.format(sftoolbox.__version__)
        about = 'Created By Sven Fraeys - 2017, All Rights Reserved'
        qtgui.QMessageBox.about(self, title, about)

    def _show_about(self):
        """show about
        """
        if not self.project:
            return

        title = '{0} - {1}'.format(self.project.label, self.project.version)
        qtgui.QMessageBox.about(self, title, self.project.about)

    def _refresh_content(self):
        """refresh the content of the panel that we are viewing
        """

        if self.project:
            self._menu_bar.setVisible(self.project.menu_bar_visible)
            self.setStyleSheet(self.project.style_sheet)
            window_title = self.project.human_name
            if self.project.version:
                window_title += " " + str(self.project.version)
            self.setWindowTitle(window_title)
            icon_filepath = self.project.absolute_icon_filepath
            if icon_filepath and os.path.exists(icon_filepath):
                icon = qtgui.QIcon(icon_filepath)
                self.setWindowIcon(icon)
            else:
                # clear the icon
                self.setWindowIcon(qtgui.QIcon())

            if self.project.active_panel:
                widget = MainPanelWidget(self.project.active_panel)
                main_widget = qtgui.QWidget()
                main_layout = qtgui.QVBoxLayout()
                main_widget.setLayout(main_layout)
                main_layout.addWidget(widget)
                self._scroll_area.setWidget(main_widget)

                # self._scroll_area.setWidget(widget)
            else:
                self._scroll_area.setWidget(qtgui.QWidget())
        else:
            self._menu_bar.setVisible(True)
            self.setStyleSheet('')
            self.setWindowTitle('SF ToolBox')
            self.setWindowIcon(qtgui.QIcon())
            self._scroll_area.setWidget(qtgui.QWidget())

    def _handle_new_panel(self):
        """handle the opening of a new panel
        """
        widget = ProjectWidget(self.project)
        self._instances.append(widget)
        widget.show()

    def _create_new_panel_action(self):
        """return action that creates a new project
        """
        action = qtgui.QAction(self)
        action.setText("New Panel...")
        action.triggered.connect(self._handle_new_panel)
        return action

    def _create_new_project_action(self):
        """return action that creates a new project
        """
        action = qtgui.QAction(self)
        action.setText("New Project...")
        action.triggered.connect(self._handle_new_project)
        return action

    def _create_editor_action(self):
        """return action that lets you browse trough all actions
        """
        action = qtgui.QAction(self)
        action.setText('Editor...')
        action.triggered.connect(self._handle_show_editor)
        return action

    def _handle_show_editor(self):
        """handle browsing trough actions
        """
        self._editor_widget.project = self.project
        self._editor_widget.show()

    def _handle_new_project(self):
        """handle creating new projects
        """
        filepath, _ = qtgui.QFileDialog.getSaveFileName(
            self, "Create new project", filter="yaml (*.yaml)")

        if not filepath:
            return

        # write the project
        open(filepath, 'w').close()

        # load it
        project = load_project_from_filepath(filepath)
        self.project = project

        utils.open_with_default_program(self.project.filepath)

        if not self.live_edit:
            answer = qtgui.QMessageBox.information(
                self, "Live Edit ?",
                "Do you want to activate Live Edit ?\n"
                "Toolbox will reload the GUI when you change the file",
                qtgui.QMessageBox.Yes | qtgui.QMessageBox.No
            )
            if answer == qtgui.QMessageBox.Yes:
                self.live_edit = True

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        if value:
            self._live_thread.filepath = value.filepath
            self._project.activate()
        self._refresh_content()

    @property
    def live_edit(self):
        return self._live_edit

    @live_edit.setter
    def live_edit(self, value):
        self._live_edit = value
        self._live_edit_action.setChecked(value)
        if value:
            self._live_thread.start()
        else:
            self._live_thread.terminate()

    def _do_update(self, value):
        new_project = load_project_from_filepath(value)
        self.project = new_project

    def __init__(self, project=None, parent=None):
        super(ProjectWidget, self).__init__(parent=parent)
        self._editor_widget = EditorWidget(project)
        self._editor_widget._panels_widget._tree.model().layoutChanged.connect(
            self._refresh_content
        )
        self._project = None
        self._live_edit = False
        self._live_thread = ReloadProjectThread()

        self._live_thread.project_changed.connect(self._do_update)
        self._live_edit_action = self._create_live_edit_action()
        self._about_action = self._create_about_action()
        self._open_project_action = self._create_open_project_action()
        self._edit_project_action = self._create_edit_project()
        self._close_project_action = self._create_close_project_action()
        self._about_toolbox_action = self._create_about_toolbox_action()
        self._new_panel_action = self._create_new_panel_action()
        self._new_project_action = self._create_new_project_action()
        self._reload_action = self._create_reload_action()
        self._close_action = self._create_close_action()
        self._actions_action = self._create_editor_action()

        menu = qtgui.QMenuBar()
        self._menu_bar = menu
        file_menu = menu.addMenu('File')
        file_menu.addAction(self._new_project_action)
        file_menu.addAction(self._open_project_action)
        file_menu.addAction(self._close_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self._reload_action)
        file_menu.addAction(self._edit_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self._new_panel_action)
        file_menu.addSeparator()
        file_menu.addAction(self._close_action)

        tools_menu = menu.addMenu('Tools')
        tools_menu.addAction(self._live_edit_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self._actions_action)
        help_menu = menu.addMenu('Help')
        help_menu.addAction(self._about_action)
        help_menu.addSeparator()
        help_menu.addAction(self._about_toolbox_action)

        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_area = self._make_scroll_area()

        self.setLayout(layout)
        layout.addWidget(menu)
        layout.addWidget(self._scroll_area)

        # set the project which will trigger the refresh
        self.project = project

    def closeEvent(self, event):
        self._live_thread.terminate()
        event.accept()

    def sizeHint(self):
        return qtcore.QSize(250, 300)

    def showEvent(self, _):
        """reload the content
        """
        self._refresh_content()
