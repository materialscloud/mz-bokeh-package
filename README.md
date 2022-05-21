# MaterialsZone Bokeh Package

## Installation
To install the latest version of this package in your current environment do:
```bash
pip install git+https://github.com/materialscloud/mz-bokeh-package.git@master
```

Or add to your `requirements.txt`/`setup.py` file the following:
```
git+https://github.com/materialscloud/mz-bokeh-package.git@master
```

## Components of the Package

### BokehUtilities
Import with:
```commandline
from mz_bokeh_package.utilites import BokehUtilities 
```
#### async_event_handler
A **decorator** that is intended to turn the loading spinner on before the execution of the decorated function, 
and turn it off when the function terminates. For this to work, your app has to provide the appropriate 
infrastructure, which is:
- a method that reacts to changes of the AppState variable `is_loading`
- the decorated function has to be a method of a class and in the class the attribute `self._doc` has to be defined 
and hold and instance of `bokeh.io.curdoc()`.

Furthermore, in the declaration of the decorated function you must not use type hints.

As an example:
```python
from bokeh.io import curdoc
from mz_bokeh_package.utilities import BokehUtilities

class DemoClass:
    def __init__(self):
        self._doc = curdoc()

    @BokehUtilities.async_event_handler
    def DemoMethod(self, an_argument, another_argument):
        # Do some calculations
        return
```
#### silent_property_change
A **function** for updating a property of a bokeh widget without triggering events bound to that property.

Example:
```python
from mz_bokeh_package.custom_widgets import CustomSelect
from mz_bokeh_package.utilities import BokehUtilities
class DemoClass:
    def __init__(self):
        self._select_widget = CustomSelect()
        self._select_widget.on_change("value", a_function)
        
        # ...
        
        BokehUtilities.silent_property_change(self._select_widget, "value", new_value)
```

## Changes and Version Number
With every PR merged into the `master` branch, add a version tag to the latest commit
and add a __short__ description of the changes in the release notes. 
The version tag has the format `vX.Y.Z` with `X`, `Y`, and `Z` being positive integer numbers, 
representing `Major Version`, `Minor Version`, and `Patch`, respectively.
Use [Semantic Versioning](https://semver.org/). This includes in particular documenting the changes.

A possible workflow for adding the version tag is checking out the `master` branch on your computer
and running the commands
```commandline
git tag vX.Y.Z
git push origin --tags
```
Then go to the `tags` page on [github](https://github.com/materialscloud/mz-bokeh-package/tags) and create a release. 
Use the tag name as release name and add a concise description of the changes in the releas notes. 
