import os
from bokeh.models.widgets.markups import Markup
from bokeh.core.properties import Bool


class CustomToggle(Markup):
    ''' Custom Toggle widget.
    '''
    __implementation__ = os.path.join("implementation_files", "toggle_btn.ts")

    __javascript__ = [
        "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
    ]

    active = Bool(default=False, help="""
    Whether the toggle button is active or not.
    """)
