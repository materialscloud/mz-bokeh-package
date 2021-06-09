from functools import partial
import inspect


class BokehUtilities:

    @staticmethod
    def async_event_handler(func):
        """This function can be used as a decorator for callbacks in order to display a loading banner
        while the callback is running.
        """

        def outer(self, *args, **kwargs):
            self._state["is_loading"] = True
            self._doc.add_next_tick_callback(partial(inner, func, self, *args, **kwargs))

        def inner(f, self, *args, **kwargs):
            f(self, *args, **kwargs)
            self._state["is_loading"] = False

        # create a version of outer that has the same signature as func (since that is expected by Bokeh)
        func_signature = str(inspect.signature(func))
        outer_with_signature_def = f"lambda {func_signature.lstrip('(').rstrip(')')}: outer{func_signature}"
        outer_with_signature = eval(outer_with_signature_def, {'outer': outer})

        return outer_with_signature

    @staticmethod
    def silent_property_change(object_name, property, value, event_handler):
        """This function allows updating any of the properties in event_handlers without triggering the event handler.
        """
        object_dict = event_handler[object_name]
        object_dict['object'].remove_on_change(property, object_dict['properties'][property])
        object_dict['object'].update_from_json({property: value})
        object_dict['object'].on_change(property, object_dict['properties'][property])
