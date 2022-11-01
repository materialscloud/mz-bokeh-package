from functools import partial
import inspect
from typing import Optional


class BokehUtilities:

    @staticmethod
    def async_event_handler(_func=None, *, function_to_execute: Optional[str] = None):
        """A decorator for event handlers to run them asynchronously and display the loading spinner while they run

        This decorator will cause the decorated event handler to run asynchronously, the loading spinner
        will be turned on while the event handler is running, and the function_to_execute will be called before the
        event handler is executed with a True parameter and after with a False parameter.
        The latter can be used, for example, to disable certain controls while the event handler is executing.

        Params:
            function_to_execute - the name of a method of the class that accepts a single boolean parameter.
            For example, there could be a method `def _disable_controls(self, disable: bool), in which case the
            string "_disable_controls" should be passed.
        """

        def _async_event_handler(func):

            def outer(self, *args, **kwargs):
                self._state["is_loading"] = True
                if function_to_execute is not None:
                    getattr(self, function_to_execute)(True)
                self._doc.add_next_tick_callback(partial(inner, func, self, *args, **kwargs))

            def inner(f, self, *args, **kwargs):
                f(self, *args, **kwargs)
                if function_to_execute is not None:
                    getattr(self, function_to_execute)(False)
                self._state["is_loading"] = False

            # create a version of outer that has the same signature as func (since that is expected by Bokeh)
            func_signature = str(inspect.signature(func))
            outer_with_signature_def = f"lambda {func_signature.lstrip('(').rstrip(')')}: outer{func_signature}"
            outer_with_signature = eval(outer_with_signature_def, {'outer': outer})

            # Add the original func (unwrapped) as a property.
            outer_with_signature._original = func

            return outer_with_signature

        if _func is None:
            return _async_event_handler
        else:
            return _async_event_handler(_func)

    @staticmethod
    def silent_property_change(widget, property, value):
        """This function allows updating a property without triggering the event handler.
        """
        callbacks = widget._callbacks[property]
        widget._callbacks[property] = []
        setattr(widget, property, value)
        widget._callbacks[property] = callbacks

    @staticmethod
    def get_document_title(session_context):
        """Returns the title of the current bokeh document.
        """
        return session_context.server_context.application_context.url[1:]
