"""This script defines a custom multiselect widget using a jQuery plugin called "bootstrap-multiselect".
For more information about the plugin: "http://davidstutz.github.io/bootstrap-multiselect"
"""
from bokeh.models import InputWidget
from bokeh.core.properties import List, Either, String, Tuple, Bool, Dict
from typing import TypeVar, Type

T = TypeVar("T", bound="CustomMultiSelectAsSingleSelect")


class CustomMultiSelectAsSingleSelect(InputWidget):
    ''' Custom Multi-select widget.
    '''
    __implementation__ = "multiselect_as_single_select.ts"
    __javascript__ = [
        "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.3/js/bootstrap.bundle.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/0.9.16/js/bootstrap-multiselect.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/js/all.min.js",
    ]
    __css__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.3/css/bootstrap.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/0.9.16/css/bootstrap-multiselect.min.css",
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
        """This function creates a custom multi select filter with a given title.
        """
        return cls(
            enable_filtering=True,
            options=[],
            value="",
            title=title,
            allow_non_selected=True,
            sizing_mode='scale_width',
            margin=[10, 10, 10, 5],
            css_classes=['custom_select', 'custom'],
        )