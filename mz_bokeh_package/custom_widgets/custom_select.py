"""This script defines a single select widget using a jQuery plugin called "bootstrap-multiselect".
For more information about the plugin: "http://davidstutz.github.io/bootstrap-multiselect"
"""
from bokeh.models import InputWidget
from bokeh.core.properties import List, Either, String, Tuple, Bool, Dict
from typing import TypeVar, Type

T = TypeVar("T", bound="CustomSelect")


class CustomSelect(InputWidget):
    ''' Custom select widget.
    '''
    __implementation__ = "select.ts"
    __javascript__ = [
        "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.2/js/bootstrap.bundle.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/1.1.2/js/bootstrap-multiselect.min.js",
    ]
    __css__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.2/css/bootstrap.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/1.1.2/css/bootstrap-multiselect.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/css/all.min.css"
    ]

    options = Either(Dict(String, List(Either(String, Tuple(String, String)))), List(Either(String, Tuple(String, String))), help="""
    Available selection options. Options may be provided either as a list of
    possible string values, or as a list of tuples, each of the form
    ``(value, label)``. In the latter case, the visible widget text for each
    value will be corresponding given label. In order to group options, provide a dictionary where each key
    is the name of a group and its corresponding value is the group options. For example:
    {"Even": ["2", "4", "6"], "Odd": ["1", "3", "5"]}. Note! the option's value should be unique across all
    other options and not only the option's group).
    """)

    value = Either(String, List(String), default="", help="""
    Initial or selected values. Note! when the options are grouped the value is a tuple
    that follows the pattern: (<group>, <value>).
    """)

    enable_filtering = Bool(default=False, help="""
    Enable filtering options using a search box.
    """)

    enabled = Bool(default=True, help="""
    Controls whether the widget is enabled (True) or disabled (False).
    Note! the "disabled" property is not supported in this widget. Use this property instead.
    """)

    non_selected_text = String(default="Select...", help="""
    The text to display on the toggle button when none of the options are selected.
    """)

    allow_non_selected = Bool(default=True, help="""
    Allows/Disallows none of the options to be selected. If set to False, the first option is selected by default.
    """)

    is_opt_grouped = Bool(readonly=True, help="""
    Indicates whether the widget contains grouped options or not.
    """)

    collapsible = Bool(default=False, help="""Allows to collapse the groups of options.""")

    collapsed_by_default = Bool(default=False, help="""Defines the state of the collapsible groups at startup.
    Can be set to True only if collapsible is activated.""")

    @classmethod
    def create(cls: Type[T], title: str) -> T:
        """This function creates a custom single select filter with the title given.
        """
        return cls(
            options=[],
            value="",
            title=title,
            enable_filtering=True,
            margin=[10, 10, 10, 5],
            allow_non_selected=True,
            sizing_mode='scale_width',
            css_classes=['custom_select', 'custom'],
        )
