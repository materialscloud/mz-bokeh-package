from bokeh.events import ButtonClick
from bokeh.io import curdoc
from bokeh.models import CustomJS, Button
from bokeh.layouts import column

from .current_user import CurrentUser


class TokenListener:
    """ A class responsible for listening to messages and updating the CurrentUser token values. """
    def __init__(self):
        self._token = None
        # add a dummy element that will trigger a token event
        self._token_button_trigger = Button(label="1", visible=False)
        self._token_button_trigger.on_event(ButtonClick, self._on_click_token_button_trigger)
        js_callback = CustomJS(
            args=dict(bokehButton=self._token_button_trigger),
            code="""
                let token_value = document.getElementById('token-invoker').getAttribute('payload')
                let tokenButton = document.evaluate(
                        "//div[@id='token-invoker']//button", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
                    ).singleNodeValue

                bokehButton.label = token_value
                tokenButton.click();
            """)
        self._token_button_trigger.js_on_change('disabled', js_callback)
        curdoc().add_periodic_callback(self._trigger_token_update, 10000)

        self.layout = column(self._token_button_trigger, name="token_trigger")

    def _trigger_token_update(self):
        self._token_button_trigger.disabled = not self._token_button_trigger.disabled

    def _on_click_token_button_trigger(self, trigger):
        self._token = self._token_button_trigger.label
        CurrentUser.update_token(self._token)
