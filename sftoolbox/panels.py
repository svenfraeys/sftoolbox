import os
import uuid
import sftoolbox.utils


class Panel(object):
    """panel to display elements in
    """

    def __init__(self, project):
        """construct the panel
        """
        project.add(self)
        self.project = project
        self.label = None
        self.description = None
        self.idname = str(uuid.uuid4())
        self.is_main_panel = False
        self.show_text = True
        self.show_icons = True
        self.icon = None
        self.style = 'vertical'
        self.style_sheet = ''

    @property
    def human_label(self):
        if self.label:
            return self.label
        else:
            return sftoolbox.utils.human_readable(str(self.idname))

    @property
    def content(self):
        """return all content belonging to the panel
        """
        content_list = []
        for content in self.project.content:
            if content.panel_idname == self.idname:
                content_list.append(content)

        # sort by weight
        content_list.sort(key=lambda x: x.weight, reverse=True)

        return content_list

    def to_json(self):
        """return the panel as a json
        """
        return {
            'label': self.label,
            'description': self.description,
            'idname': self.idname,
            'is_main_panel': self.is_main_panel,
            'show_text': self.show_text,
            'show_icons': self.show_icons,
            'style': self.style,
            'icon': self.icon,
            'style_sheet': self.style_sheet
        }

    @classmethod
    def from_json(cls, project, data):
        """load from json
        """
        panel = cls(project)
        panel.label = data.get('label')
        panel.description = data.get('description')

        # add the idname prefix if needed
        panel.idname = data.get('idname')
        panel.is_main_panel = data.get('is_main_panel')
        panel.show_text = data.get('show_text', True)
        panel.show_icons = data.get('show_icons', True)
        panel.style = data.get('style', 'vertical')
        panel.icon = data.get('icon')
        panel.style_sheet = data.get('style_sheet', '')

        # load in the actions define in the panel
        actions = data.get('actions')
        if actions:
            if isinstance(actions, dict):
                action_list = []
                for idname, action in actions.items():
                    if isinstance(action, basestring):
                        action = {'description': action}
                    if action is None:
                        action = {}

                    action.setdefault('idname', idname)
                    action_list.append(action)
                actions = action_list
            elif isinstance(actions, basestring):
                actions = [{'idname': actions}]

            for action in actions:
                # import here for double import error
                import sftoolbox.actions
                import sftoolbox.content

                if not isinstance(action, dict):
                    action = {'idname': str(action)}

                # add idname prefix of this current panel
                original_idname = action['idname']
                action['idname'] = panel.idname + '.' + original_idname

                if 'label' not in action:
                    action['label'] = sftoolbox.utils.human_readable(
                        str(original_idname))

                action_instance = sftoolbox.actions.action_from_json(project,
                                                                     action)
                content_i = sftoolbox.content.ActionContent(project)
                content_i.weight = action.get('weight', 0)
                content_i.panel = panel
                content_i.target_action = action_instance

        content = data.get('content')
        if content:
            if isinstance(content, dict):
                content_list = []
                for idname, content_i in content.items():
                    content_i.setdefault('idname', idname)
                    content_list.append(content_i)
                content = content_list

            for content_i in content:
                # import here to avoid double error
                import sftoolbox.content

                if 'label' not in content_i:
                    content_i['label'] = sftoolbox.utils.human_readable(
                        str(content_i['idname']))
                content_i['idname'] = panel.idname + '.' + content_i['idname']
                content_i = sftoolbox.content.content_from_json(project, content_i)
                content_i.panel = panel

        panels = data.get('panels')
        if panels:
            if isinstance(panels, dict):
                panel_list = []
                for idname, panel_i in panels.items():
                    panel_i.setdefault('idname', idname)
                    panel_list.append(panel_i)
                panels = panel_list
            elif isinstance(panels, basestring):
                panels = [{'idname': panels}]

            for panel_data in panels:
                # import here for double import error
                import sftoolbox.content

                if 'label' not in panel_data:
                    panel_data['label'] = sftoolbox.utils.human_readable(
                        str(panel_data['idname']))

                # add panel
                panel_data['idname'] = panel.idname + '.' + panel_data[
                    'idname']
                panel_i = cls.from_json(project, panel_data)
                content = sftoolbox.content.PanelContent(project)
                content.panel = panel
                content.target_panel = panel_i

        return panel

    @property
    def absolute_icon_filepath(self):
        if not self.icon:
            return None
        return os.path.join(self.project.directory, self.icon)

    def __repr__(self):
        return '<Panel {0}>'.format(self.idname)
