from bokeh.io import curdoc
from bokeh.models import Column, Row, Div
from mz_bokeh_package.custom_widgets import CustomMultiSelect, CustomMultiSelectAsSingleSelect, CustomSelect

explanation = """<p>This panel shows all boolean options for the CustomSelect and for the
CustomMultiSelect widgets. </p>
<p> Note that some combinations don't work, e.g. you cannot have the <i>select_all</i>, the <i>collapsible</i>,
and the <i>collapsed_by_default</i> option active at the same time - in this case the Select All button is not
responding, or more specifically: The Select All button selects only those sub-items that are expanded.
If you collapse one group and open another, then press "Select All", only those items from the open group are selected.
</p>
<p> Note that the collapsed_by_default is ignored if collapsible is not activated. </p>
"""

options = {"Group 1": [["id1.1", "Title 1.1"], ["id1.2", "Title 1.2"]],
           "Group 2": [["id2.1", "Title 2.1"], ["id2.2", "Title 2.2"]]
           }

boolean_attributes_ms = ["enabled", "enable_filtering", "include_select_all", "collapsible", "collapsed_by_default"]
boolean_attributes_single = ["enabled", "enable_filtering", "allow_non_selected"]
boolean_attributes_ms_as_single = boolean_attributes_single + ["collapsible", "collapsed_by_default"]


def on_change(attr, old, new):
    print(f"Callback for attribute {attr} -- old selection: {old}\n"
          f"                                new selection: {new}")


def create_custom_widgets_with_switched_boolean_attributes(widget: CustomSelect | CustomMultiSelect,
                                                           attributes: list[str], name):
    list_of_widgets = [widget.create(title=f"{name}, default settings")]

    for attr in attributes:
        list_of_widgets.append(widget.create(title=""))
        non_default_ms = not getattr(list_of_widgets[-1], attr)
        setattr(list_of_widgets[-1], attr, non_default_ms)
        list_of_widgets[-1].title = f"{name}, {attr} {'activated' if non_default_ms else 'deactivated'}"

    return list_of_widgets


select_widgets = create_custom_widgets_with_switched_boolean_attributes(CustomSelect,
                                                                        boolean_attributes_single, "CustomSelect")
multi_select_widgets = create_custom_widgets_with_switched_boolean_attributes(CustomMultiSelect,
                                                                              boolean_attributes_ms,
                                                                              "CustomMultiSelect")
single_multi_select_widgets = create_custom_widgets_with_switched_boolean_attributes(CustomMultiSelectAsSingleSelect,
                                                                                     boolean_attributes_ms_as_single,
                                                                                     "CustomMultiSelectAsSingle")


multi_select_widgets.append(CustomMultiSelect.create(title="CustomMultiSelect, collapsible AND collapsed_by_default"))
multi_select_widgets[-1].collapsible = True
multi_select_widgets[-1].collapsed_by_default = True

single_multi_select_widgets.append(CustomMultiSelectAsSingleSelect.create(title="CustomMultiSelectAsSingle, "
                                                                                "collapsible AND collapsed_by_default"))
single_multi_select_widgets[-1].collapsible = True
single_multi_select_widgets[-1].collapsed_by_default = True

for widget in multi_select_widgets + select_widgets + single_multi_select_widgets:
    widget.options = options
    widget.on_change("value", on_change)

curdoc().add_root(
    Column(
        Div(text=explanation, width=600),
        Row(
            Column(*select_widgets),
            Column(*multi_select_widgets),
            Column(*single_multi_select_widgets)
        )
    )
)
