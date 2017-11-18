"""engine containing and managing each component
"""
import os
import sys
import yaml

import sftoolbox.panels
import sftoolbox.actions
import sftoolbox.content
import sftoolbox.variables


class Project(object):
    """engine
    """

    def __init__(self, filepath=None):
        """engine collecting all information
        """
        self.filepath = filepath
        self.label = None
        self.version = None
        self.description = None
        self.active_panel_idname = None
        self.about = ''
        self.style_sheet = ''
        self.sys_path = []

        self.actions = []
        self.content = []
        self.panels = []
        self.menu_bar_visible = True
        self._load_project()

    @property
    def directory(self):
        """open the directory
        """
        return os.path.dirname(self.filepath)

    @property
    def absolute_icon_filepath(self):
        if self.icon_filepath:
            return os.path.join(self.directory, self.icon_filepath)

    @property
    def human_name(self):
        if self.label:
            return self.label

        return os.path.splitext(os.path.basename(self.filepath))[0]

    def _load_project(self):
        """load in the project from the directory data
        """
        if not self.filepath or not os.path.exists(self.filepath):
            return

        with open(self.filepath, 'r') as fp:
            data = yaml.load(fp)

        if data is None:
            data = {}

        # if string just use it as a name
        if isinstance(data, basestring):
            data = {'label': data}

        self.label = data.get('label')
        self.description = data.get('description')
        self.active_panel_idname = data.get('active_panel')
        self.about = data.get('about')
        self.version = data.get('version')
        self.icon_filepath = data.get('icon')
        self.style_sheet = data.get('style_sheet', '')
        self.menu_bar_visible = data.get('menu_bar_visible', True)
        sys_path = data.get('sys_path', ['.'])
        if isinstance(sys_path, basestring):
            sys_path = [sys_path]

        self.sys_path = sys_path

        variables = data.get('variables', [])

        # register all variables
        for variable in variables:
            sftoolbox.variables.from_json(self, variable)

        # load actions
        actions = data.get('actions', [])
        if isinstance(actions, dict):
            action_list = []
            for idname, action in actions.items():
                action.setdefault('idname', idname)
                action_list.append(action)
            actions = action_list
        elif isinstance(actions, basestring):
            actions = [{'idname': actions}]

        for action_dict in actions:
            sftoolbox.actions.action_from_json(self, action_dict)

        # load panels

        panels = data.get('panels', [])

        if isinstance(panels, dict):
            panel_list = []
            for idname, panel in panels.items():
                if isinstance(panel, basestring):
                    panel = {'idname': panel}
                panel.setdefault('idname', idname)
                panel_list.append(panel)
            panels = panel_list
        elif isinstance(panels, basestring):
            panels = [{'idname': panels}]

        # add the main panel
        main_panel = data.get('main')
        if main_panel:
            if isinstance(main_panel, basestring):
                main_panel = {'idname': 'main', 'descriptoin': main_panel}
            elif isinstance(main_panel, dict):
                main_panel.setdefault('idname', 'main')

            panels.insert(0, main_panel)

        if panels and not self.active_panel_idname:
            self.active_panel_idname = panels[0].get('idname')

        for panel_dict in panels:
            sftoolbox.panels.Panel.from_json(self, panel_dict)

        # load content
        content = data.get('content', [])
        if isinstance(content, dict):
            content_list = []
            for idname, content_i in content.items():
                content_i.setdefault('idname', idname)
                content_list.append(content_i)
            content = content_list

        for content_dict in content:
            sftoolbox.content.content_from_json(self, content_dict)

    def add(self, value):
        """add a given element
        """
        if isinstance(value, sftoolbox.panels.Panel):
            self.panels.append(value)
        elif isinstance(value, sftoolbox.actions.Action):
            self.actions.append(value)
        elif isinstance(value, sftoolbox.content.Content):
            self.content.append(value)

    def apply_sys_path(self):
        """apply adding the sys path
        """
        for sys_path in self.sys_path:
            sys_path = os.path.join(os.path.dirname(self.filepath), sys_path)
            sys_path = os.path.abspath(sys_path)
            sys.path.append(sys_path)

    def activate(self):
        """activate the project in the current session
        """
        self.apply_sys_path()

    @property
    def active_panel(self):
        for panel in self.panels:
            if panel.idname == self.active_panel_idname:
                return panel

    @active_panel.setter
    def active_panel(self, value):
        if value:
            self.active_panel_idname = value.idname
        else:
            self.active_panel_idname = None
