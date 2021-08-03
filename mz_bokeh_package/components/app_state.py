import json
from typing import Callable, List, Dict, Any, Optional
from functools import partial
from bokeh.models import Toggle, CustomJS
from bokeh.io import curdoc

from mz_bokeh_package.utilities import BokehUtilities


class AppStateValue():

    def __init__(self):
        self._value: Any = None
        self._callback_functions: List[Callable] = []
        self.persistent = False

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

    def __init__(self, cookies: Optional[Dict[str, Any]] = None):
        self._doc = curdoc()
        self._values: Dict[str, AppStateValue] = {}
        self._cookies = self._get_cookies()

    def __getitem__(self, key) -> Any:
        return self._values[key].value

    def __setitem__(self, key, value):
        if key not in self._values:
            self._values[key] = AppStateValue()
        self._values[key].value = value

    def __contains__(self, key) -> bool:
        return key in self._values

    def on_change(self, key: str, callback_function: Callable):
        """ assign a callback function to a stored value

        Args:
            key: a unique key identifying your stored value
            callback_function: the function to call when the value of the stored value changes
        """
        if key not in self._values:
            self._values[key] = AppStateValue()
        self._values[key].subscribe(callback_function)

    def _add_cookie_saver_to_doc(self):
        """Adds a dummy bokeh widget to the bokeh document.

        This dummy widget can be used to store cookies using a JS callback.
        """
        cookie_saver = Toggle(visible=False, name="cookie_saver")
        cookie_saver.js_on_change("active", CustomJS(code=""))
        self._doc.add_root(cookie_saver)

    def set_persistent_value(self, key: str):
        app_state_value = self._values.get(key) or AppStateValue()
        app_state_value.value = self._cookies.get(key)
        app_state_value.persistent = True
        self.on_change(key, partial(self._store_cookie_callback, cookie_name=key))

        if not self._doc.select_one({"name": "cookie_saver"}):
            self._add_cookie_saver_to_doc()

    def _store_cookie_callback(self, data, cookie_name):
        """Stores data to a HTTP cookie.

        This callback is used for persistent AppStateValue instances.
        Each time the value of persistent instances changes, this callback stores
        the new value as a HTTP cookie.
        """
        document_title = BokehUtilities.get_document_title(self._doc.session_context)
        cookie_value = data if isinstance(data, str) else str(data).replace("'", '"')
        cookie_saver = curdoc().select_one({"name": "cookie_saver"})
        cookie_saver.js_property_callbacks["change:active"][0].code = f"""
        document.cookie = '{document_title}_{cookie_name}={cookie_value}'
        """
        cookie_saver.active = not cookie_saver.active

    def _get_cookies(self) -> Dict[str, Any]:
        """Fetches dashboard-related cookies.

        Returns:
            Dict[str, Any]: HTTP cookies dictionary.
        """
        session_context = self._doc.session_context
        cookies = session_context.request.cookies
        dashboard_title = BokehUtilities.get_document_title(session_context)

        cookies = {}
        for cookie_name, cookie_value in cookies.items():
            if cookie_name.startswith(dashboard_title):
                key = cookie_name.replace(f"{dashboard_title}_", "")

                try:
                    value = json.loads(cookie_value)
                except json.JSONDecodeError:
                    value = cookie_value

                cookies[key] = value

        return cookies
