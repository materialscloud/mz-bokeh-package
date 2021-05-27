from typing import Callable, List, Dict, Any
from bokeh.models.widgets.markups import Div
from bokeh.models import CustomJS
from bokeh.layouts import column

from mz_bokeh_package.custom_widgets.select import CustomMultiSelect, CustomSelect  # noqa F401


class LoadingSpinner:

    def __init__(self):
        # add a dummy element that will trigger the event for enabling/disabling the loading spinner
        self._loader_trigger = Div(text="1", visible=False)
        self._callback = CustomJS(code="")
        self._loader_trigger.js_on_change('text', self._callback)
        self._enabled = True

        self.layout = column(self._loader_trigger, name="loaderTrigger")

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """enable/disable loading mode """
        self._enabled = value
        self._callback.code = f"""
                    document.getElementById('loaderContainer').style.visibility = '{'visible' if value else 'hidden'}';
                """
        self._loader_trigger.text = str(int(self._loader_trigger.text) + 1)


class AppStateValue():

    def __init__(self):
        self._value: Any = None
        self._callback_functions: List[Callable] = []

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        try:
            if self._value == new_value:
                return
        except ValueError:
            pass
        self._value = new_value
        self._call_callbacks()

    def subscribe(self, callback_function: Callable):
        self._callback_functions.append(callback_function)

    def _call_callbacks(self):
        for callback_function in self._callback_functions:
            callback_function(self.value)


class AppState:
    """ This class is used to store data that is shared by different components in the app.
    For example, if one component is used to calculate the area under a plot and another one is used to save that
    area as a sample, then the state object can store the value "plot_area". An app should hold (at most) a single
    instance of this class.

    Usage:
        # initialize a single instance of the class in your App class
        state = AppState()

        # create a callback function that will be called every time a certain value changes
        def callback_function(value):
            print(value)

        # assign the callback function to a stored value
        state.on_change("plot_area", callback_function)

        # change the value of your stored value, the callback function will be called only when the value changes
        state["plot_area"] = 1
        state["plot_area"] = 2
        state["plot_area"] = 2
        state["plot_area"] = 1

        # this will print:
        # 1
        # 2
        # 1

        # print the current value of your stored value
        print(state["plot_area"])
    """

    def __init__(self):
        self._values: Dict[str, AppStateValue] = {}

    def __getitem__(self, key) -> Any:
        return self._values[key].value

    def __setitem__(self, key, value):
        if key not in self._values:
            self._values[key] = AppStateValue()
        self._values[key].value = value

    def on_change(self, key: str, callback_function: Callable):
        """ assign a callback function to a stored value

        Args:
            key: a unique key identifying your stored value
            callback_function: the function to call when the value of the stored value changes
        """
        if key not in self._values:
            self._values[key] = AppStateValue()
        self._values[key].subscribe(callback_function)
