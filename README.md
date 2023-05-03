## MaterialsZone Bokeh Package

### 1. Installation
To install the latest version of this package in your current environment do:
```bash
pip install git+https://github.com/materialscloud/mz-bokeh-package.git@master
```

Or add to your `requirements.txt`/`setup.py` file the following:
```
git+https://github.com/materialscloud/mz-bokeh-package.git@master
```

To install a branch during development, replace `master` with the branch name.
This will work for both options above.

### 2. User Authentication

To access the dashboards, user authentication is mandatory and requires setting up of the User API Key.
The method for obtaining the User API Key varies depending on the environment setting.

On **development**, set the following environment variables:
```
ENVIRONMENT=dev
API_KEY=<API key>
```

On **staging** or **production**, set the following environment variable ```ENVIRONMENT=`staging` or `production` ```
and provide the API key via the URL arguments. For example: `http://localhost:5006/correlation?api_key=valid_key` 

### 3. Authentication Module Development

For development and testing of the authentication module, define the `--auth-module` when running the Bokeh server as follows:
```
bokeh serve <relative path of dashboard> --auth-module=<full path to auth.py>
```

For example:
```
bokeh serve dashboards/histogram --auth-module=<root path>/data-overview-apps/venv/lib/python3.10/site-packages/mz_bokeh_package/authentication/auth.py
```

### 4. Changes and Version Number
With every PR merged into the `master` branch, please add a version tag to the latest commit
and add a __short__ description of the changes to the file `CHANGES.md` (newer entries at the top).