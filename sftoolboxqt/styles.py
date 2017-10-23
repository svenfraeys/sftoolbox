from sftoolboxqt import qtgui
from sftoolboxqt import engine


@engine.register_style_class
class GridStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'grid'

    def __init__(self, parent=None):
        super(GridStyle, self).__init__(parent=parent)
        self.item_count = 0
        self.max_lines = 3
        self.row = 0
        self.column = 0
        self.direction = 'vertical'

        layout = qtgui.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def add_content_widget(self, content_widget):
        """add the content
        """
        if self.direction == 'vertical':
            self.layout().addWidget(content_widget, self.row, self.column)
        else:
            self.layout().addWidget(content_widget, self.column, self.row)
        self.item_count += 1
        self.column += 1
        if self.column >= self.max_lines:
            self.column = 0
            self.row += 1


@engine.register_style_class
class HorizontalStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'horizontal'

    def __init__(self, parent=None):
        super(HorizontalStyle, self).__init__(parent=parent)
        layout = qtgui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def add_content_widget(self, content_widget):
        """add the content
        """
        self.layout().addWidget(content_widget)


@engine.register_style_class
class VerticalStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'vertical'

    def __init__(self, parent=None):
        super(VerticalStyle, self).__init__(parent=parent)
        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def add_content_widget(self, content_widget):
        """add the content
        """
        self.layout().addWidget(content_widget)


def create_style(style_type, args=None, kwargs=None):
    """create a style with the given name
    """
    for class_ in engine.style_classes_register:
        if class_.json_type == style_type:
            if not args:
                args = []
            if not kwargs:
                kwargs = {}

            return class_(*args, **kwargs)
