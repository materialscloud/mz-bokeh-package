"""This module includes the PlotSettings class that implements a plot tool that
allows modifying various properties of the plot.
"""
import os
import re
import itertools
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from bokeh.io import curdoc
from bokeh.plotting import Figure
from bokeh.core.enums import Anchor
from bokeh.palettes import Category10
from bokeh.models import (
    CustomAction,
    Spinner,
    Button,
    CheckboxGroup,
    CustomJS,
    Column,
    Toggle,
)

from mz_bokeh_package.components import AppState
from mz_bokeh_package.custom_widgets import CustomSelect, CustomMultiSelect

BASE_DIR = os.path.dirname(__file__)

# Use the Bokeh's Category10 palette and additional custom colors in the palette.
COLORS_PALETTE = (
    *Category10[10][:-2],
    "#4d4e4f",
    Category10[10][-2],
    "#c3ecf4",
    "#00bcd4",
)
COLORS_NAMES = [
    "Blue",
    "Orange",
    "Green",
    "Red",
    "Purple",
    "Brown",
    "Pink",
    "Gray",
    "Dark Gray",
    "Lime Green",
    "Light Turquoise",
    "Dark Turquoise",
]
POINT_COLORS = {color: name for color, name in zip(COLORS_PALETTE, COLORS_NAMES)}
AXES_WIDTH_ATTRIBUTES = {"axis_line_width", "major_tick_line_width", "minor_tick_line_width"}
AXES_NORMAL_WIDTH = 1
AXES_BOLD_WIDTH = 2
LINE_NORMAL_WIDTH = 0.8
LINE_BOLD_WIDTH = 2
PLOT_DIMENSION_STEP = 50
PLOT_DIMENSION_MIN = 300
PLOT_DIMENSION_MAX = 1500
LEGEND_POSITIONS = [position for position in Anchor if "_" in position]
POINT_SHAPES = [
    "asterisk",
    "circle",
    "circle_cross",
    "circle_dot",
    "circle_y",
    "circle_x",
    "cross",
    "dash",
    "diamond",
    "diamond_cross",
    "diamond_dot",
    "dot",
    "hex",
    "hex_dot",
    "inverted_triangle",
    "plus",
    "square",
    "square_cross",
    "square_dot",
    "square_pin",
    "square_x",
    "star",
    "star_dot",
    "triangle",
    "triangle_dot",
    "x",
    "y",
]
PLOT_DIMENSIONS_SETTINGS = ["custom_plot_dimensions", "plot_height", "plot_width"]
BASE_SETTINGS = ["grid_lines", "plot_outline", "axes_thickness", *PLOT_DIMENSIONS_SETTINGS]


def get_options_from_ids(ids: List[str]) -> List[Tuple[str]]:
    """Creates a list of options for a given list of option IDs.

    Args:
        ids (List[str]): A list of option IDs.

    Returns:
        List[Tuple[str]]: A list of tuples in the format (<option_id>, <option_label>).
    """
    return [(id, id.replace("_", " ").title()) for id in ids]


SETTINGS = {
    "grid_lines": (CheckboxGroup, {"labels": ["Grid Lines"]}),
    "plot_outline": (CheckboxGroup, {"labels": ["Plot Outline"]}),
    "custom_plot_dimensions": (CheckboxGroup, {"labels": ["Custom Plot Dimensions:"]}),  # noqa: E501
    "plot_height": (Spinner, {"title": "Height (pixels)", "low": PLOT_DIMENSION_MIN, "high": PLOT_DIMENSION_MAX, "step": PLOT_DIMENSION_STEP, "disabled": True, "css_classes": ["plot-dimensions"]}),  # noqa: E501
    "plot_width": (Spinner, {"title": "Width (pixels)", "low": PLOT_DIMENSION_MIN, "high": PLOT_DIMENSION_MAX, "step": PLOT_DIMENSION_STEP, "disabled": True, "css_classes": ["plot-dimensions"]}),  # noqa: E501
    "text_size": (Spinner, {"title": "Text size", "low": 0, "high": 100, "step": 1, "value": 0}),
    "point_size": (Spinner, {"title": "Point size", "low": 0, "high": 100, "step": 1, "value": 0}),
    "point_shape": (CustomSelect, {"title": "Point shape", "options": get_options_from_ids(POINT_SHAPES), "allow_non_selected": False}),  # noqa: E501
    "point_color": (CustomSelect, {"title": "Point color", "options": [*POINT_COLORS.items()], "allow_non_selected": False}),  # noqa: E501
    "multi_point_color": (CustomMultiSelect, {"title": "Point colors", "options": [*POINT_COLORS.items()]}),  # noqa: E501
    "text_thickness": (CheckboxGroup, {"labels": ["Bold Text"]}),
    "axes_thickness": (CheckboxGroup, {"labels": ["Bold Axes"]}),
    "line_thickness": (CheckboxGroup, {"labels": ["Bold Line"]}),
    "line_color": (CustomSelect, {"title": "Line color", "options": [*POINT_COLORS.items()], "allow_non_selected": False}),  # noqa: E501
    "multi_line_color": (CustomMultiSelect, {"title": "Line colors", "options": [*POINT_COLORS.items()], }),  # noqa: E501
    "fill_color": (CustomSelect, {"title": "Fill color", "options": [*POINT_COLORS.items()], "allow_non_selected": False}),  # noqa: E501
    "show_legend": (CheckboxGroup, {"labels": ["Legend"]}),
    "legend_position": (CustomSelect, {"title": "Legend Position", "options": get_options_from_ids(LEGEND_POSITIONS), "allow_non_selected": False}),  # noqa: E501
}


class PlotSettings:
    """This class contains widgets and logic that are common to all settings modals.
    """
    default_values = {
        "grid_lines": True,
        "plot_outline": False,
        "custom_plot_dimensions": False,
        "plot_height": 600,
        "plot_width": 600,
        "text_size": 11,
        "point_size": 8,
        "point_shape": "circle",
        "point_color": COLORS_PALETTE[0],  # Blue
        "multi_point_color": [COLORS_PALETTE[0]],  # Blue
        "text_thickness": False,
        "axes_thickness": False,
        "line_thickness": False,
        "line_color": COLORS_PALETTE[7],  # Gray
        "multi_line_color": [COLORS_PALETTE[0]],  # Blue
        "fill_color": COLORS_PALETTE[-2],  # Light Turquoise
        "show_legend": True,
        "legend_position": "top_right",
    }

    def __init__(
        self,
        title: str,
        plot: Figure,
        state: AppState,
        included_settings: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes a PlotSettings instance.

        Args:
            title (str): The title of the plot settings modal.
            plot (Figure): The plot to apply the settings to.
            state (AppState): Bokeh application state.
            included_settings (Optional[List[str]], optional): A list of setting IDs to include in the settings modal.
                The order in which the settings widgets are rendered matches the order they appear in this list.
                Defaults to None.
            default_values (Optional[Dict[str, Any]], optional): A dictionary that maps settings to
                their default values. For example, {"show_legend": False}. Defaults to None.
            configure_jinja_env (bool, optional): Whether to configure the jinja environment or not. Defaults to True.
        """

        self._title = title
        self._plot = plot
        self._state = state
        self._included_settings = included_settings or BASE_SETTINGS
        self._plot_tool_description = "Plot Settings"

        # Update settings' default values
        if default_values:
            self.default_values.update(default_values)

        # Initialize settings' widgets
        self._init_included_widgets()

        # Create a dummy widget to allow invoking a backend callback (python) from the frontend (javascript)
        self._backend_callback_invoker = Toggle()
        self._backend_callback_invoker.on_change("active", self._update_widgets_values)

        # Add the settings tool to the plot
        self._settings_plot_tool = CustomAction(
            description=self._plot_tool_description,
            icon=os.path.join(BASE_DIR, "../assets/img/settings-icon.png"),
            callback=self._get_settings_button_click_js_callback(),
        )
        self._plot.add_tools(self._settings_plot_tool)

        # "Apply" button
        self._apply_dialog_btn = Button(
            label="Apply",
            width=75,
            css_classes=["apply-plot-settings"],
            name="apply_btn",
        )
        self._apply_dialog_btn.on_click(self.on_apply_dialog)

        # "Cancel" button
        self._cancel_dialog_btn = Button(
            label="Cancel",
            width=75,
            css_classes=["cancel-plot-settings"],
            name="cancel_btn",
        )
        self._cancel_dialog_btn.on_click(self._on_cancel_dialog)

        # "Reset" button
        # Note! This button is an icon button that uses google fonts.
        # the "label" property holds the name of the icon that is used.
        # More info can be found in "https://google.github.io/material-design-icons".
        self._reset_btn = Button(
            label="restart_alt",
            width=42,
            css_classes=["reset-plot-settings"],
            name="reset_btn",
        )
        self._reset_btn.on_click(self._on_reset_settings)

        # Layout the widgets
        self.layout = Column(
            *(self._get_setting_widget(setting_id) for setting_id in self._included_settings),
            self._apply_dialog_btn,
            self._cancel_dialog_btn,
            self._reset_btn,
        )

        # Set plot properties' initial values
        self._init_plot_settings_values()

        self._configure_jinja_environment()

    @property
    def _plot_settings_state(self) -> Dict[str, Any]:
        state_cookie = self._state["plot_settings_state"] or {}

        return {
            setting_id: state_cookie.get(setting_id) or self.default_values.get(setting_id)
            for setting_id in self._included_settings
        }

    @_plot_settings_state.setter
    def _plot_settings_state(self, value: Dict[str, Any]):
        self._state["plot_settings_state"] = value

    @property
    def _grid_lines(self) -> bool:
        return all(grid.visible for grid in self._plot.grid)

    @_grid_lines.setter
    def _grid_lines(self, value: bool):
        self._plot.grid[0].visible = value
        self._plot.grid[1].visible = value

    @property
    def _plot_outline(self) -> bool:
        return bool(self._plot.outline_line_alpha)

    @_plot_outline.setter
    def _plot_outline(self, value: bool):
        if value:
            axes_width = AXES_BOLD_WIDTH if self._get_setting_widget_value("axes_thickness") else AXES_NORMAL_WIDTH
            outline_width = axes_width if "axes_thickness" in self._included_settings else AXES_NORMAL_WIDTH
            self._plot.outline_line_dash = "solid"
            self._plot.outline_line_color = "black"
            self._plot.outline_line_alpha = 1
            self._plot.outline_line_width = outline_width
        else:
            self._plot.outline_line_alpha = 0

    @property
    def _custom_plot_dimensions(self) -> bool:
        return self._plot.sizing_mode is None

    @_custom_plot_dimensions.setter
    def _custom_plot_dimensions(self, value: bool):
        self._plot.sizing_mode = None if value else "scale_width"
        self._plot.aspect_ratio = "auto" if value else 1.5

    @property
    def _plot_height(self) -> Optional[int]:
        return PLOT_DIMENSION_STEP * round(self._plot.outer_height / PLOT_DIMENSION_STEP)

    @_plot_height.setter
    def _plot_height(self, value: Optional[int]):
        self._plot.height_policy = "auto"
        self._plot.height = value

    @property
    def _plot_width(self) -> Optional[int]:
        return PLOT_DIMENSION_STEP * round(self._plot.outer_width / PLOT_DIMENSION_STEP)

    @_plot_width.setter
    def _plot_width(self, value: Optional[int]):
        self._plot.width_policy = "auto"
        self._plot.width = value

    @property
    def _text_size(self) -> float:
        font_size_str = self._plot.xaxis.major_label_text_font_size

        # Extracts the numerical value of the font-size out of the font-size string (e.g "12px").
        return float(re.split(r"[px|pt]", font_size_str, 1)[0])

    @_text_size.setter
    def _text_size(self, value: float):
        self._plot.xaxis.major_label_text_font_size = f"{value}px"
        self._plot.yaxis.major_label_text_font_size = f"{value}px"
        self._plot.xaxis.axis_label_text_font_size = f"{value}px"
        self._plot.yaxis.axis_label_text_font_size = f"{value}px"

    @property
    def _point_size(self) -> float:
        return self._plot.renderers[0].glyph.size

    @_point_size.setter
    def _point_size(self, value: float):
        self._plot.renderers[0].glyph.size = value

    @property
    def _point_shape(self) -> str:
        glyph = self._plot.renderers[0].glyph
        glyph_class_name = type(glyph).__name__.lower()
        return getattr(glyph, "marker", glyph_class_name)

    @_point_shape.setter
    def _point_shape(self, value: str):
        # Fetch the glyph renderer's "create" method
        create_glyph = getattr(self._plot, value)

        # Get glyphs kwargs
        glyph_kwargs = self._get_glyph_kwargs()

        fill_alpha = 0 if value.endswith(("_dot", "_cross", "_y", "_x")) else 1

        for kwargs in glyph_kwargs:
            # The "Circle" glyph has no "marker" attribute,
            # hence it should be removed from kwargs.
            if value == "circle":
                kwargs.pop("marker", None)

            kwargs["fill_alpha"] = fill_alpha

            # Create the glyph renderer
            create_glyph(**kwargs)

        # remove previous renderers
        self._plot.renderers = self._plot.renderers[len(glyph_kwargs):]

        # Update legend
        if getattr(self._plot, "legend"):
            for renderer, legend_item in zip(self._plot.renderers, self._plot.legend.items):
                legend_item.renderers = [renderer]

    @property
    def _point_color(self) -> str:
        return self._plot.renderers[0].glyph.fill_color

    @_point_color.setter
    def _point_color(self, value: str):
        for renderer in self._plot.renderers:
            renderer.glyph.line_color = value
            renderer.glyph.fill_color = value

    @property
    def _text_thickness(self) -> bool:
        return self._plot.xaxis.major_label_text_font_style == "bold" and \
            self._plot.xaxis.axis_label_text_font_style == "bold" and \
            self._plot.yaxis.major_label_text_font_style == "bold" and \
            self._plot.yaxis.axis_label_text_font_style == "bold"

    @_text_thickness.setter
    def _text_thickness(self, value: bool):
        label_style = "bold" if value else "normal"
        self._plot.xaxis.major_label_text_font_style = label_style
        self._plot.yaxis.major_label_text_font_style = label_style
        self._plot.xaxis.axis_label_text_font_style = label_style
        self._plot.yaxis.axis_label_text_font_style = label_style

    @property
    def _axes_thickness(self) -> bool:
        return all(
            getattr(axis, attr) == AXES_BOLD_WIDTH
            for axis in self._plot.axis
            for attr in AXES_WIDTH_ATTRIBUTES
        )

    @_axes_thickness.setter
    def _axes_thickness(self, value: bool):
        axis_width = AXES_BOLD_WIDTH if value else AXES_NORMAL_WIDTH
        kwargs = {attr: axis_width for attr in AXES_WIDTH_ATTRIBUTES}
        for axis in self._plot.axis:
            axis.update(**kwargs)

    @property
    def _line_thickness(self) -> bool:
        renderer = self._plot.renderers[0]
        return renderer.glyph.line_width == LINE_BOLD_WIDTH and \
            renderer.hover_glyph.line_width == LINE_BOLD_WIDTH

    @_line_thickness.setter
    def _line_thickness(self, value: bool):
        line_width = LINE_BOLD_WIDTH if value else LINE_NORMAL_WIDTH
        renderer = self._plot.renderers[0]
        renderer.glyph.line_width = line_width
        renderer.hover_glyph.line_width = line_width

    @property
    def _line_color(self) -> str:
        return self._plot.renderers[0].glyph.line_color

    @_line_color.setter
    def _line_color(self, value: str):
        for renderer in self._plot.renderers:
            renderer.glyph.line_color = value

            if hasattr(renderer.hover_glyph, "line_color"):
                renderer.hover_glyph.line_color = self._find_darker_shade(value)

    @property
    def _multi_line_color(self) -> List[str]:
        renderers_num = len(self._plot.renderers)

        if renderers_num == 1:
            renderer = self._plot.renderers[0]
            color_field_name = renderer.glyph.line_color
            return [*{*renderer.data_source.data[color_field_name]}]
        else:
            return [renderer.glyph.line_color for renderer in self._plot.renderers]

    @_multi_line_color.setter
    def _multi_line_color(self, value: List[str]):
        renderers_num = len(self._plot.renderers)
        if renderers_num == 1:
            self._set_colors_by_field(value)

        else:
            colors = self._fill_missing_colors(value, len(self._plot.renderers))

            for color, renderer in zip(colors, self._plot.renderers):
                renderer.glyph.line_color = color

                if getattr(renderer, "hover_glyph"):
                    renderer.hover_glyph.line_color = self._find_darker_shade(color)

    @property
    def _multi_point_color(self) -> List[str]:
        renderers_num = len(self._plot.renderers)

        if renderers_num == 1:
            renderer = self._plot.renderers[0]
            color_field_name = renderer.glyph.fill_color
            return [*{*renderer.data_source.data[color_field_name]}]
        else:
            return [renderer.glyph.fill_color for renderer in self._plot.renderers]

    @_multi_point_color.setter
    def _multi_point_color(self, value: List[str]):
        renderers_num = len(self._plot.renderers)

        if renderers_num == 1:
            self._set_colors_by_field(value)

        else:
            colors = self._fill_missing_colors(value, len(self._plot.renderers))

            for color, renderer in zip(colors, self._plot.renderers):
                renderer.glyph.fill_color = color
                renderer.glyph.line_color = color

                if getattr(renderer, "hover_glyph"):
                    darker_shade = self._find_darker_shade(color)
                    renderer.hover_glyph.fill_color = darker_shade
                    renderer.hover_glyph.line_color = darker_shade

    @property
    def _fill_color(self) -> str:
        return self._plot.renderers[0].glyph.fill_color

    @_fill_color.setter
    def _fill_color(self, value: str):
        for renderer in self._plot.renderers:
            if hasattr(renderer.glyph, "fill_color"):
                renderer.glyph.fill_color = value

            if hasattr(renderer.hover_glyph, "fill_color"):
                renderer.hover_glyph.fill_color = self._find_darker_shade(value)

    @property
    def _show_legend(self) -> bool:
        return self._plot.legend.visible

    @_show_legend.setter
    def _show_legend(self, value: bool):
        self._plot.legend.visible = value

    @property
    def _legend_position(self) -> str:
        return self._plot.legend.location

    @_legend_position.setter
    def _legend_position(self, value: str):
        self._plot.legend.location = value

    def _init_included_widgets(self):
        """Initializes Bokeh widgets based on included settings.
        """
        for setting_id in self._included_settings:
            widget_class, kwargs = SETTINGS[setting_id]

            if widget_class.__name__ == "CheckboxGroup":
                kwargs["css_classes"] = ["custom_checkbox"]

            setting_widget = widget_class(**kwargs)
            setting_widget.name = setting_id

            if setting_id == "custom_plot_dimensions":
                setting_widget.on_change("active", self._toggle_plot_dimensions)

            setattr(self, f"_{setting_id}_widget", setting_widget)

    def _get_settings_button_click_js_callback(self) -> CustomJS:
        """Returns a javascript callback to run when the settings tool is clicked.

        Returns:
            CustomJS: "on_click" Javascript callback.
        """

        args = {"backend_callback_invoker": self._backend_callback_invoker}
        code = f"""
        // Add "data" attributes to the "Settings" tool to allow toggling the modal.
        $(".bk-toolbar-button-custom-action[title='{self._plot_tool_description}']").attr("data-toggle", "modal")
            .attr("data-target", "#plot-settings-modal")

        // Add "data" attribute to both the "Apply" and "Cancel" buttons (in the modal) to allow closing the modal.
        $(".apply-plot-settings > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")
        $(".cancel-plot-settings > .bk-btn-group > .bk-btn").attr("data-dismiss", "modal")

        // Add a tooltip to the "Reset" button (in the modal).
        $(".reset-plot-settings > .bk-btn-group > .bk-btn").attr("data-toggle", "tooltip")
            .attr("title", "Reset to Default")

        // Add an icon for the "Reset" button.
        $(".reset-plot-settings > .bk-btn-group > .bk-btn:not([class*='material-icons'])").addClass("material-icons")
        $(".reset-plot-settings > .bk-btn-group > .bk-btn").removeClass("bk bk-btn-default")

        // Invoke backend callback
        backend_callback_invoker.active = !backend_callback_invoker.active
        """
        return CustomJS(args=args, code=code)

    def on_apply_dialog(self, new_plot: Optional[Figure] = None):
        """Modifies the plot based on the settings configurations.

        This method can be triggered either by clicking the "Apply" button in the settings modal
        or by another component that replaces the existing plot with a new one and needs to apply the settings on
        the newly created plot. For example, updating the "Parameter to Display" filter in the "Histogram" dashboard
        causes a creation of a new Figure instance. In such case, the histogram component can use this function
        in order to apply the plot settings on the newly created plot.

        Args:
            new_plot (Optional[Figure], optional): The newly created Figure instance. Defaults to None.
        """
        if isinstance(new_plot, Figure):
            self._plot = new_plot
            self._plot.add_tools(self._settings_plot_tool)

        state = {}

        for setting_id in self._included_settings:
            value = self._get_setting_widget_value(setting_id)

            # Update the plot based on the applied setting
            self._set_setting_property(setting_id, value)

            state[setting_id] = value

        # Save the state as a cookie
        self._plot_settings_state = state

    def _on_cancel_dialog(self):
        for setting_id in self._included_settings:
            setting_value = self._plot_settings_state[setting_id]
            self._set_setting_widget_value(setting_id, setting_value)

    def _on_reset_settings(self):
        for setting_id in self._included_settings:
            setting_value = self.default_values[setting_id]
            self._set_setting_widget_value(setting_id, setting_value)

    def _configure_jinja_environment(self):
        """Configures the Bokeh template's environment.

        These configurations:
            1. Allow the Bokeh template that is used to render the app to import/include the settings modal macros
                by adding their path to Jinja's search path.
            2. Add template variables that are necessary for running the settings modal macros.
        """

        PLOT_SETTINGS_MACROS_PATH = os.path.join(BASE_DIR, "../templates/plot_settings_modal")
        doc = curdoc()

        # Add the settings modal macros directory to the Jinja environment search path.
        # This allows importing/including the settings modal macros in the Bokeh app template.
        doc.template.environment.loader.searchpath.append(PLOT_SETTINGS_MACROS_PATH)

        # Add template variables. These variables are necessary for generating the settings modal HTML.
        doc.template_variables["plot_settings_title"] = self._title
        doc.template_variables["plot_settings_layout"] = [
            self._get_setting_widget(setting_id).name
            for setting_id in self._included_settings
        ]

    def _get_setting_widget(self, setting_id: str) -> Any:
        """Returns the corresponding Bokeh widget of a given setting.

        Args:
            setting_id (str): ID of a setting.

        Returns:
            Any: The setting's corresponding Bokeh widget.
        """
        return getattr(self, f"_{setting_id}_widget", None)

    def _get_setting_widget_value(self, setting_id: str) -> Any:
        """Returns the value of the corresponding Bokeh widget of a given setting.

        Args:
            setting_id (str): ID of a setting.

        Returns:
            Any: The value of the setting's corresponding Bokeh widget.
        """
        setting_widget = getattr(self, f"_{setting_id}_widget", None)

        if setting_widget is None:
            raise ValueError(f"The setting '{setting_id}' has no corresponding widget")

        if type(setting_widget).__name__ == "CheckboxGroup":
            return bool(setting_widget.active)
        else:
            return setting_widget.value

    def _set_setting_property(self, setting_id: str, value: Any):
        """Sets the value of the corresponding class property of a given setting.

        Args:
            setting_id (str): ID of the setting.
            value (Any): Value to set to the corresponding class property.
        """
        setattr(self, f"_{setting_id}", value)

    def _set_setting_widget_value(self, setting_id: str, value: Any):
        """Sets the value of the corresponding widget of a given setting.

        Args:
            setting_id (str): ID of the setting.
            value (Any): Value to set to the corresponding widget.
        """
        setting_widget = self._get_setting_widget(setting_id)

        if type(setting_widget).__name__ == "CheckboxGroup":
            setting_widget.active = [0] if value else []
        else:
            setting_widget.value = value

    def _get_setting_property(self, setting_id: str) -> Any:
        return getattr(self, f"_{setting_id}")

    def _get_glyph_kwargs(self) -> List[Dict[str, Any]]:
        """Returns the keyword arguments of each of the plot's renderers.

        Returns:
            List[Dict[str, Any]]: A list of renderers' keyword arguments.
        """
        if len(self._plot.renderers) == 0:
            return []

        return [
            {
                **renderer.glyph._property_values,
                "source": renderer.data_source,
                "visible": renderer.visible,
            }
            for renderer in self._plot.renderers
        ]

    def _init_plot_settings_values(self):
        """Initializes the settings values.

        The initial values are set to be equal to the last saved state (loaded by the AppState).
        If there is no saved state, they are default to the "default_values" class property.
        """
        for setting_id, value in self._plot_settings_state.items():
            self._set_setting_property(setting_id, value)
            self._set_setting_widget_value(setting_id, value)

    @staticmethod
    def _find_darker_shade(color: str) -> str:
        """Finds a darker shade for a given hex color.

        Args:
            color (str): A valid hex color (e.g "#4F4F4F").

        Returns:
            str: A darker hex color.
        """
        MIN = 0
        MAX = 255
        DELTA = 30
        hex_color = color.lstrip("#")

        # For each of the RGB parts, find a darker shade by decreasing the value (by "DELTA") and
        # concatenate the results back together. Each result is being clipped to (MIN, MAX)
        # in order to keep it valid.
        return "#" + "".join(
            "{:02x}".format(np.clip(int(hex_color[i:i+2], 16) - DELTA, MIN, MAX))
            for i in (0, 2, 4)
        )

    def _set_colors_by_field(self, colors: List[str]):
        """Sets plot colors by modifying a data source field.

        This method assumes that the plot's data is grouped using Bokeh's
        "automatic grouping" feature (more info here: https://docs.bokeh.org/en/latest/docs/user_guide/annotations.html#automatic-grouping-browser-side)
        rather than having multiple renderers.

        Args:
            colors (List[str]): A list of colors that were chosen by the user in the settings modal.
        """  # noqa: E501

        renderer = self._plot.renderers[0]
        source = renderer.data_source
        data = source.data
        color_field_name = getattr(renderer, "fill_color", renderer.glyph.line_color)

        # The field that the data is grouped by
        grouped_by = self._plot.legend.items[0].label["field"]

        groups = {*data[grouped_by]}
        groups_colors = self._fill_missing_colors(colors, len(groups))

        # Set color for each group
        criteria = [np.array(data[grouped_by]) == group_name for group_name in groups]
        data[color_field_name] = np.select(criteria, groups_colors)

    def _fill_missing_colors(self, chosen_colors: List[str], groups_num: int) -> List[str]:
        """Fills missing colors.

        In case there are more groups to be colored than colors that were chosen by the user,
        the function will add the missing colors.

        Args:
            chosen_colors (List[str]): Colors that were chosen by the user.
            groups_num (int): Groups to be colored.

        Returns:
            List[str]: A list with the same number of colors as the number of groups.
        """
        # There are enough colors to color all the groups.
        if len(chosen_colors) >= groups_num:
            return chosen_colors[:groups_num]

        # Colors that were not chosen by the user
        not_chosen_colors = [color for color in COLORS_PALETTE if color not in chosen_colors]

        # Creating an infinite pool of colors (repetitive) while giving precedence to colors
        # that were not chosen by the user.
        colors_pool = itertools.cycle(not_chosen_colors + chosen_colors)

        # Number of missing colors
        missing_colors_num = groups_num-len(chosen_colors)

        return chosen_colors + [next(colors_pool) for _ in range(missing_colors_num)]

    def _update_widgets_values(self, attr, old, new):
        """Updates the widgets' values based on the current state of the plot.
        """
        for setting_id in self._included_settings:
            setting_value = self._get_setting_property(setting_id)
            self._set_setting_widget_value(setting_id, setting_value)

    def _toggle_plot_dimensions(self, attr, old, new):
        """Enables/disables the "plot height" and "plot width" widgets.
        """
        is_disabled = False if new else True
        self._get_setting_widget("plot_height").disabled = is_disabled
        self._get_setting_widget("plot_width").disabled = is_disabled
