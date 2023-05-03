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

To access the dashboards, user authentication is mandatory and involves two steps.

#### 2.1. Define the `--auth-module` when running the Bokeh server.
```
bokeh serve <relative path of dashboard> --auth-module=<full path to mz_bokeh_package/utilities/auth.py>
```
For example:
```
bokeh serve dashboards/histogram --auth-module=<root path>/data-overview-apps/venv/lib/python3.10/site-packages/mz_bokeh_package/utilities/auth.py. If you are running the dashboard using a configuration in PyCharm, then set the Module Name to bokeh, the Parameters to serve <full path of dashboard>.
```

#### 2.2. Set up the User API Key.

There are two pathways to obtain user authentication.

On **development**, set the following environment variables:
```
ENVIRONMENT=dev
API_KEY=<API key>
```

On **staging** or **production**, set the following environment variable ```ENVIRONMENT=`staging` or `production` ```
and provide the API key via the URL arguments. For example: `http://localhost:5006/correlation?api_key=valid_key` 



### 3. Changes and Version Number
With every PR merged into the `master` branch, please add a version tag to the latest commit
and add a __short__ description of the changes to the file `CHANGES.md` (newer entries at the top).