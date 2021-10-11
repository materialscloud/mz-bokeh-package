import pytest
from typing import Any
from mz_bokeh_package.components import AppStateValue


def test_construction():
    app_state_value = AppStateValue()
    assert app_state_value.value is None

    app_state_value = AppStateValue(3)
    assert app_state_value.value == 3


def test_set_value():
    app_state_value = AppStateValue()
    assert not app_state_value.value

    app_state_value.value = 3
    assert app_state_value.value == 3


def dummy_callback_no_args() -> None:
    pass


def dummy_callback_one_arg(new_value: Any) -> None:
    pass


def dummy_callback_two_args(new_value: Any, other_value: Any) -> None:
    pass


class DummyComponent():
    values = []

    def method_no_args(self) -> None:
        pass

    def method_one_arg(self, new_value: Any) -> None:
        self.values.append(new_value)

    def method_two_args(self, new_value: Any, other_value: Any) -> None:
        pass

    @staticmethod
    def static_method_no_args() -> None:
        pass

    @staticmethod
    def static_method_one_arg(new_value: Any) -> None:
        pass

    @staticmethod
    def static_method_two_args(new_value: Any, other_value: Any) -> None:
        pass

    @classmethod
    def class_method_no_args(cls) -> None:
        pass

    @classmethod
    def class_method_one_arg(cls, new_value: Any) -> None:
        pass

    @classmethod
    def class_method_two_args(cls, new_value: Any, other_value: Any) -> None:
        pass


def test_subscribe():

    app_state_value = AppStateValue()
    component = DummyComponent()

    # Callbacks without arguments exceptions
    for invalid_callback in [
        dummy_callback_no_args,
        component.method_no_args,
        component.static_method_no_args,
        component.class_method_no_args,
    ]:
        with pytest.raises(ValueError):
            app_state_value.subscribe(invalid_callback)

    # Callbacks with two arguments exceptions
    for invalid_callback in [
        dummy_callback_two_args,
        component.method_two_args,
        component.static_method_two_args,
        component.class_method_two_args,
    ]:
        with pytest.raises(ValueError):
            app_state_value.subscribe(invalid_callback)

    # Callbacks with a single argument do not raise exceptions
    for valid_callback in [
        dummy_callback_one_arg,
        component.method_one_arg,
        component.static_method_one_arg,
        component.class_method_one_arg,
    ]:
        app_state_value.subscribe(valid_callback)


def test_change_value_with_callback():

    app_state_value = AppStateValue(3)
    component = DummyComponent()

    app_state_value.subscribe(component.method_one_arg)

    # On value change
    app_state_value.value = 4
    assert component.values == [4]

    # Value did not change
    app_state_value.value = 4
    assert component.values == [4]

    # Two callbacks subscribed
    app_state_value.subscribe(component.method_one_arg)
    app_state_value.value = 5
    assert component.values == [4, 5, 5]
