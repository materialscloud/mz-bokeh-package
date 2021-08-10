import pytest
from typing import Any
from mz_bokeh_package.components import AppStateValue


def test_construction():
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


class DummyComponent():
    values = []

    def callback_no_args(self) -> None:
        pass

    def callback_one_arg(self, new_value) -> None:
        self.values.append(new_value)


def test_subscribe():

    app_state_value = AppStateValue()

    # Add non-member functions as callbacks
    with pytest.raises(ValueError):
        app_state_value.subscribe(dummy_callback_no_args)

    app_state_value.subscribe(dummy_callback_one_arg)

    # Add member functions as callbacks
    component = DummyComponent()

    with pytest.raises(ValueError):
        app_state_value.subscribe(component.callback_no_args)

    app_state_value.subscribe(component.callback_one_arg)


def test_change_value_with_callback():

    app_state_value = AppStateValue(3)
    component = DummyComponent()

    app_state_value.subscribe(component.callback_one_arg)

    # On value change
    app_state_value.value = 4
    assert component.values == [4]

    # Value did not change
    app_state_value.value = 4
    assert component.values == [4]

    # Two callbacks subscribed
    app_state_value.subscribe(component.callback_one_arg)
    app_state_value.value = 5
    assert component.values == [4, 5, 5]
