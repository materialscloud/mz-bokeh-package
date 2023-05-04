## MaterialsZone Bokeh Package

This package offers common functionality that can be used in Materials Zone Bokeh app repos.
Included in this repo are the following sub-packages and resources:
1. utilities package - a collection of classes and modules that can be used for fetching the identity of the current
   user, fetching environment-specific, and more.
2. auth.py module - a module that is used for authenticating with Materials Zone (see the docstring of the auth.py 
   module for instructions).
3. components package - common components including the AppState class, ConfirmationModal, LoadingSpinner, and 
   PlotSettings.
4. custom_widgets - custom widgets including custom select, custom multiselect, and custom toggle.
5. assets directory - common assets such as icons.


### 1. Installing the mz-bokeh-package in a repo
To install a specific version of this package in the environment of your Bokeh app repo, add the following to your 
`requirements.txt`/`setup.py`/`pyproject.toml` file:
```
git+https://github.com/materialscloud/mz-bokeh-package.git@<version-number>
```
Replace `<version-number>` with the tag of the version you would like to install.

Note: to install a branch during development of the mz-bokeh-package, replace `<version-number>` with the branch name.


### 2. Development
To create a new version of mz-bokeh-package, update the version number in the setup.py file in a dedicated commit, add
a tag to the `master` branch by first checking out the branch, and then running the command:
```bash
git tag <version-number> -am <version description>
```
Then, push the tag:
```bash
git push <version-number>
```


