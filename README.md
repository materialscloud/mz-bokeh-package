## MaterialsZone Bokeh Package

### 1. Installation
To install the latest version of this package in your current environment do:
```bash
pip install git+https://github.com/materialscloud/mz-bokeh-package.git@<version-number>
```

Or add to your `requirements.txt`/`setup.py`/`pyproject.toml` file the following:
```
git+https://github.com/materialscloud/mz-bokeh-package.git@<version-number>
```

To install a branch during development, replace `<version-number>` with the branch name.
This will work for both options above.

### 2. User Authentication

To access the dashboards, user authentication is mandatory. The authentication process varies depending on the chosen environment.

On **development**, provide the User API Key as an environment variable:
```
API_KEY=<API key>
```

On **staging/production**, define the `--auth-module` when running the Bokeh server as follows:
```
bokeh serve <relative path of dashboard> --auth-module=<full path to auth.py>
```

For example:
```
bokeh serve dashboards/histogram --auth-module=<root path>/data-overview-apps/venv/lib/python3.10/site-packages/mz_bokeh_package/authentication/auth.py
```

To provide the User API Key, it must be included in the URL arguments.
For example: `http://localhost:5006/histogram?api_key=valid_key`


### 4. Changes and Version Number
With every PR merged into the `master` branch, please add a version tag to the latest commit
and add a __short__ description to it.