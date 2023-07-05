from bokeh.io import curdoc
from bokeh.models.layouts import Column, Row
from mz_bokeh_package.custom_widgets import CustomMultiSelect, CustomSelect

options = {"Group 1": [["id1.1", "Title 1.1"], ["id1.2", "Title 1.2"]],
           "Group 2": [["id2.1", "Title 2.1"], ["id2.2", "Title 2.2"]]
           }

boolean_attributes_ms = ["enabled", "enable_filtering", "include_select_all", "collapsible", "collapsed_by_default"]
boolean_attributes_single = ["enabled", "enable_filtering", "allow_non_selected", "collapsible", "collapsed_by_default"]

select_widgets = [CustomSelect.create(title="CustomSelect, default settings")]
multi_select_widgets = [CustomMultiSelect.create(title="CustomMultiSelect, default settings")]


def on_change(attr, old, new):
    print(f"Callback for attribute {attr} -- old selection: {old}\n"
          f"                                new selection: {new}")


for attr in boolean_attributes_ms:
    multi_select_widgets.append(CustomMultiSelect.create(title=""))
    non_default_ms = not getattr(multi_select_widgets[-1], attr)
    setattr(multi_select_widgets[-1], attr, non_default_ms)
    multi_select_widgets[-1].title = f"CustomMultiSelect, {attr} {'activated' if non_default_ms else 'deactivated'}"

multi_select_widgets.append(CustomMultiSelect.create(title="CustomMultiSelect, collapsible AND collapsed_by_default"))
multi_select_widgets[-1].collapsible = True
multi_select_widgets[-1].collapsed_by_default = True

for attr in boolean_attributes_single:
    select_widgets.append(CustomSelect.create(title=""))
    non_default_single = not getattr(select_widgets[-1], attr)
    setattr(select_widgets[-1], attr, non_default_single)
    select_widgets[-1].title = f"Select, {attr} {'activated' if non_default_single else 'deactivated'}"

select_widgets.append(CustomSelect.create(title="Select, collapsible AND collapsed_by_default"))
select_widgets[-1].collapsible = True
select_widgets[-1].collapsed_by_default = True

for widget in multi_select_widgets + select_widgets:
    widget.options = options
    widget.on_change("value", on_change)

curdoc().add_root(Row(Column(*select_widgets),  Column(*multi_select_widgets)))
