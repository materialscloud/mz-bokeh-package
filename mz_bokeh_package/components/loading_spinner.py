import logging
from bokeh.models.widgets.markups import Div
from bokeh.models import CustomJS
from bokeh.layouts import column

logger = logging.getLogger(__name__)


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
        visibility = 'visible' if value else 'hidden'
        self._callback.code = f"""
            document.getElementById('loading-spinner-invoker').style.visibility = '{visibility}';
        """
        logger.debug(f"Loading spinner is {visibility}")
        self._loader_trigger.text = str(int(self._loader_trigger.text) + 1)
