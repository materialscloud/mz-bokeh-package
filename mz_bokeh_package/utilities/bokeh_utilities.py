from functools import partial


class BokehUtilities:

    @staticmethod
    def async_event_handler(func):
        """This function can be used as a decorator for callbacks in order to display a loading banner
        while the callback is running.
        """

        def outer(self, attr, old, new):
            self._state["is_loading"] = True
            self._doc.add_next_tick_callback(partial(inner, func, self, attr, old, new))

        def inner(f, self, attr, old, new):
            f(self, attr, old, new)
            self._state["is_loading"] = False

        return outer

    @staticmethod
    def silent_property_change(object_name, property, value, event_handler):
        """This function allows updating any of the properties in event_handlers without triggering the event handler.
        """
        object_dict = event_handler[object_name]
        object_dict['object'].remove_on_change(property, object_dict['properties'][property])
        object_dict['object'].update_from_json({property: value})
        object_dict['object'].on_change(property, object_dict['properties'][property])
