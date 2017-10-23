"""widgets available for toolbox
"""
import functools
import os

import sftoolbox
import sftoolbox.content
from sftoolbox.project import Project
from sftoolboxqt import qtgui
from sftoolboxqt import qtcore
from sftoolboxqt.styles import create_style
import sftoolbox.utils


class ReloadProjectThread(qtcore.QThread):
    """reload live project
    """
    project_changed = qtcore.Signal(str)

    def __init__(self):
        super(ReloadProjectThread, self).__init__()
        self.project_directory = None
        self.previous_hash = None

    @property
    def toolbox_yaml(self):
        if not self.project_directory:
            return ''
        return os.path.join(self.project_directory, 'toolbox.yaml')

    def run(self):
        import time
        while True:
            time.sleep(1)
            if os.path.exists(self.toolbox_yaml):
                current_hash = sftoolbox.utils.get_hash_from_file(
                    self.toolbox_yaml)
                if self.previous_hash != current_hash:
                    self.previous_hash = current_hash
                    self.project_changed.emit(self.project_directory)


class ActionWidget(qtgui.QWidget):
    """action button
    """

    def __init__(self, action=None, show_text=True, show_icons=True,
                 parent=None):
        super(ActionWidget, self).__init__(parent=parent)
        self.action = action
        self._button = qtgui.QPushButton()
        self.show_text = show_text
        self.show_icons = show_icons

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

            self.setWindowTitle(self.action.label)
            self._button.setToolTip(self.action.description)
            self._button.setStatusTip(self.action.description)
            self._button.clicked.connect(self._handle_click)

            icon_filepath = self.action.absolute_icon_filepath
            if self.show_icons:
                if icon_filepath and os.path.exists(icon_filepath):
                    self._button.setIcon(qtgui.QIcon(icon_filepath))

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
                 parent=None):
        """construct the button
        """
        super(ContentWidget, self).__init__(parent=parent)
        self.content = content
        self.show_text = show_text
        self.show_icons = show_icons

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
                                  show_text=self.show_text)

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

        self.style = create_style(panel.style)

        layout = qtgui.QVBoxLayout()

        layout.addWidget(self.style)

        self.setLayout(layout)
        self._refresh_content()

    def _refresh_content(self):
        """refresh the content of the panel
        """
        if self.panel:
            self.setWindowTitle(self.panel.human_label)
            self.setToolTip(self.panel.description)
            self.setStatusTip(self.panel.description)

            for content in self.panel.content:
                content_widget = ContentWidget(content, self.panel.show_icons,
                                               self.panel.show_text)
                self.style.add_content_widget(content_widget)


class MainPanelWidget(PanelWidget):
    """panel widget that is going to be the one floating around
    """

    def _refresh_content(self):
        super(MainPanelWidget, self)._refresh_content()
        layout = self.layout()
        spacer = qtgui.QSpacerItem(0, 0, qtgui.QSizePolicy.Minimum,
                                   qtgui.QSizePolicy.MinimumExpanding)
        layout.addItem(spacer)


class ProjectWidget(qtgui.QWidget):
    """toolbox main window
    """

    def _handle_about_to_show_panels(self):
        self.panels_menu.clear()
        if not self.project:
            return

        for panel in self.project.panels:
            if not panel.is_main_panel:
                continue

            action = qtgui.QAction(self)
            action.setText(panel.human_label)
            callback = functools.partial(self._set_active_panel, panel)
            action.triggered.connect(callback)
            self.panels_menu.addAction(action)

            if self.active_panel == panel:
                action.setCheckable(True)
                action.setChecked(True)

    def _set_active_panel(self, value):
        self.project.active_panel = value
        self.active_panel = self.project.active_panel

    @property
    def active_panel(self):
        return self._active_panel

    @active_panel.setter
    def active_panel(self, value):
        """set the active panel
        """
        self._active_panel = value

        if value:
            widget = MainPanelWidget(value)
            self._scroll_area.setWidget(widget)
        else:
            self._scroll_area.setWidget(qtgui.QWidget())

    def _make_scroll_area(self):
        """return the scroll area
        """
        scroll_area = qtgui.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(qtgui.QFrame.NoFrame)
        return scroll_area

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
        directory = qtgui.QFileDialog.getExistingDirectory(self,
                                                           "Select Project Directory...")
        if not directory:
            return
        project = sftoolbox.project.Project(directory)
        self.project = project

    def _create_about_action(self):
        action = qtgui.QAction(self)
        action.setText('About')
        action.triggered.connect(self._show_about)
        return action

    def _create_about_toolbox_action(self):
        action = qtgui.QAction(self)
        action.setText('About SF Tool Box')
        action.triggered.connect(self._show_about_tool_box)
        return action

    def _create_reload_action(self):
        action = qtgui.QAction(self)
        action.setText('Reload Project')
        action.triggered.connect(self._handle_reload)
        return action

    def _handle_reload(self):
        """handle reload
        """
        if self.project:
            return

        project = Project(self.project.directory)
        self.project = project

    def _create_close_action(self):
        """create a close action
        """
        action = qtgui.QAction(self)
        action.setText("Close")
        action.triggered.connect(self.close)
        return action

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

        title = '{0} - {1}'.format(self.project.name, self.project.version)
        qtgui.QMessageBox.about(self, title, self.project.about)

    def _refresh_content(self):
        if self.project:
            self.setWindowTitle(self.project.name)
            self.active_panel = self.project.active_panel
            icon_filepath = self.project.absolute_icon_filepath
            if icon_filepath and os.path.exists(icon_filepath):
                icon = qtgui.QIcon(icon_filepath)
                self.setWindowIcon(icon)
        else:
            self.setWindowTitle('SF ToolBox')
            self.setWindowIcon(qtgui.QIcon())
            self.active_panel = None

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        if value:
            self._live_thread.project_directory = value.directory
        self._refresh_content()

    @property
    def live_edit(self):
        return self._live_edit

    @live_edit.setter
    def live_edit(self, value):
        self._live_edit = value

    def _do_update(self, value):
        new_project = Project(value)
        self.project = new_project

    def __init__(self, project=None, parent=None):
        super(ProjectWidget, self).__init__(parent=parent)
        self._project = project
        self._live_edit = False
        self._active_panel = None
        self._live_thread = ReloadProjectThread()
        if self._project:
            self._live_thread.project_directory = self._project.directory

        self._live_thread.project_changed.connect(self._do_update)
        self._live_thread.start()

        self._about_action = self._create_about_action()
        self._open_project_action = self._create_open_project_action()
        self._close_project_action = self._create_close_project_action()
        self._about_toolbox_action = self._create_about_toolbox_action()
        self._reload_action = self._create_reload_action()
        self._close_action = self._create_close_action()

        menu = qtgui.QMenuBar()
        file_menu = menu.addMenu('File')
        file_menu.addAction(self._open_project_action)
        file_menu.addAction(self._close_project_action)
        file_menu.addAction(self._reload_action)
        file_menu.addSeparator()
        file_menu.addAction(self._close_action)
        self.panels_menu = menu.addMenu('Panels')
        help_menu = menu.addMenu('Help')
        help_menu.addAction(self._about_action)
        help_menu.addSeparator()
        help_menu.addAction(self._about_toolbox_action)
        self.panels_menu.aboutToShow.connect(self._handle_about_to_show_panels)

        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_area = self._make_scroll_area()

        self.setLayout(layout)
        layout.addWidget(menu)
        layout.addWidget(self._scroll_area)

        # set the active panel
        self._refresh_content()
