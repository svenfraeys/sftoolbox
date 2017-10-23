"""engine containing and managing each component
"""
import os

import sftoolbox.panels
import sftoolbox.actions
import sftoolbox.content
import yaml


class Project(object):
    """engine
    """

    def __init__(self, directory=None):
        """engine collecting all information
        """
        self.name = None
        self.version = None
        self.description = None
        self.directory = directory
        self.active_panel_idname = None
        self.about = ''

        self.actions = []
        self.content = []
        self.panels = []
        self._load_project()

    @property
    def absolute_icon_filepath(self):
        if self.icon_filepath:
            return os.path.join(self.directory, self.icon_filepath)

    def _load_project(self):
        """load in the project from the directory data
        """
        yaml_filepath = os.path.join(self.directory, 'toolbox.yaml')

        with open(yaml_filepath, 'r') as fp:
            data = yaml.load(fp)

        self.name = data.get('name')
        self.description = data.get('description')
        self.active_panel_idname = data.get('active_panel')
        self.about = data.get('about')
        self.version = data.get('version')
        self.icon_filepath = data.get('icon')

        # load actions
        actions = data.get('actions', [])
        if isinstance(actions, dict):
            action_list = []
            for idname, action in actions.items():
                action.setdefault('idname', idname)
                action_list.append(action)
            actions = action_list

        for action_dict in actions:
            sftoolbox.actions.from_json(self, action_dict)

        # load panels
        panels = data.get('panels', [])
        if isinstance(panels, dict):
            panel_list = []
            for idname, panel in panels.items():
                panel.setdefault('idname', idname)
                panel_list.append(panel)
            panels = panel_list

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
            sftoolbox.content.from_json(self, content_dict)

    def add(self, value):
        """add a given element
        """
        if isinstance(value, sftoolbox.panels.Panel):
            self.panels.append(value)
        elif isinstance(value, sftoolbox.actions.Action):
            self.actions.append(value)
        elif isinstance(value, sftoolbox.content.Content):
            self.content.append(value)

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