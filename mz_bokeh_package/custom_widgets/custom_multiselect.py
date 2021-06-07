"""This script defines a custom multiselect widget using a jQuery plugin called "bootstrap-multiselect".
For more information about the plugin: "http://davidstutz.github.io/bootstrap-multiselect"
"""
import os
from bokeh.models import InputWidget
from bokeh.core.properties import List, Either, String, Tuple, Bool, Int, Nullable, Dict
from typing import TypeVar, Type

T = TypeVar("T", bound="CustomMultiSelect")


class CustomMultiSelect(InputWidget):
    ''' Custom Multi-select widget.
    '''
    __implementation__ = os.path.join("implementation_files", "multiselect.ts")
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

    value = Nullable(List(Either(String, List(String))), help="""
    Initial or selected values. Note! when the options are grouped the value is a list of tuples
    that follow the pattern: (<group>, <value>).
    """)

    include_select_all = Bool(default=False, help="""
    Whether to include a "Select All" option or not. Note! in order to initialize the widget
    with the "Select All" option checked, set the "select_all" property to True.
    """)

    select_all = Bool(default=False, help="""
    Whether all the options are selected or not. Note! this property is valid also when the
    "include_select_all" property is set to false.
    """)

    number_displayed = Int(default=1, help="""
    Determines how many selected labels should be displayed on the toggle button.
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

    is_opt_grouped = Bool(readonly=True, help="""
    Indicates whether the widget contains grouped options or not.
    """)

    dropdown_closed = Bool(default=False, help="""
    This property changes right before the "value" property changes.
    """)

    @classmethod
    def create(cls: Type[T], title: str) -> T:
        """This function creates a custom multi select filter with a given title.
        """
        return cls(
            include_select_all=True,
            enable_filtering=True,
            options=[],
            value=[],
            title=title,
            sizing_mode='scale_width',
            margin=[10, 10, 10, 5],
            css_classes=['custom_select', 'custom']
        )
