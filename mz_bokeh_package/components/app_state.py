import json
from inspect import getfullargspec, ismethod
from typing import Callable, Iterable, List, Dict, Any, Optional
from functools import partial
from bokeh.models import Toggle, CustomJS
from bokeh.io import curdoc

from mz_bokeh_package.utilities import BokehUtilities, Environment, CurrentUser


class AppStateValue():

    def __init__(self, value: Optional[Any] = None):
        self._value = value
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

    def subscribe(self, callback_function: Callable[[Any], None]):
        callback_signature = getfullargspec(callback_function)

        function_arguments = callback_signature.args
        if ismethod(callback_function) or (isinstance(callback_function, partial) and ismethod(callback_function.func)):
            function_arguments.pop(0)

        if len(function_arguments) != 1:
            raise ValueError(
                f"Callback functions require a single argument (new_value), but the provided "
                f"callback has {len(callback_signature.args)} arguments."
            )

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

    def __init__(self, persistent_keys: Optional[Iterable[str]] = None):
        self._doc = curdoc()
        self._values: Dict[str, AppStateValue] = {}

        if persistent_keys:
            self._add_persistent_values(persistent_keys)

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

    def _set_persistent_value(self, key: str, value: Optional[Any] = None):
        self[key] = value
        self.on_change(key, partial(self._store_cookie_callback, cookie_name=key))

    def _store_cookie_callback(self, data, cookie_name):
        """Stores data to a HTTP cookie.

        This callback is used for persistent AppStateValue instances.
        Each time the value of persistent instances changes, this callback stores
        the new value as a HTTP cookie.
        """
        dashboard_title = BokehUtilities.get_document_title(self._doc.session_context)
        user_id = CurrentUser().get_user_key()
        cookie_value = data if isinstance(data, str) else json.dumps(data)
        env = Environment.get_environment()
        cookie_saver = curdoc().select_one({"name": "cookie_saver"})

        if env == "dev":
            code = f"""
            document.cookie = '{user_id}_{dashboard_title}_{cookie_name}={cookie_value};SameSite=None;Secure'
            """
        else:
            code = f"""
            document.cookie = '{user_id}_{dashboard_title}_{cookie_name}={cookie_value};Domain=.materials.zone;SameSite=None;Secure'
            """  # noqa: E501

        cookie_saver.js_property_callbacks["change:active"][0].code = code
        cookie_saver.active = not cookie_saver.active

    def _get_cookies(self) -> Dict[str, Any]:
        """Fetches dashboard-related cookies.

        Returns:
            Dict[str, Any]: HTTP cookies dictionary.
        """
        session_context = self._doc.session_context
        request_cookies = session_context.request.cookies
        dashboard_title = BokehUtilities.get_document_title(session_context)
        user_id = CurrentUser().get_user_key()
        cookies_prefix = f"{user_id}_{dashboard_title}_"

        dashboard_cookies = {}
        for cookie_name, cookie_value in request_cookies.items():
            if cookie_name.startswith(cookies_prefix):
                key = cookie_name.replace(cookies_prefix, "")

                try:
                    value = json.loads(cookie_value)
                except json.JSONDecodeError:
                    value = cookie_value

                dashboard_cookies[key] = value

        return dashboard_cookies

    def _add_persistent_values(self, persistent_keys: Iterable[str]):
        cookies = self._get_cookies()

        for key in persistent_keys:
            self._set_persistent_value(key, cookies.get(key))

        self._add_cookie_saver_to_doc()
