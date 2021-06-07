from bokeh.io import curdoc
from bokeh.models.layouts import Column
from mz_bokeh_package.components import CustomMultiSelect, CustomSelect

ms = CustomMultiSelect.create(title="RoiWeinreb")
ss = CustomSelect.create(title="Roi")


def on_change(attr, old, new):
    print(old, new)


ms.on_change("value", on_change)
ss.on_change("value", on_change)

curdoc().add_root(Column(ms, ss))
