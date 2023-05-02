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

## User Authentication

User authentication is a mandatory requirement to access the dashboards.
There are two pathways to obtain user authentication.

On **development**, set the following environment variables:
```
ENVIRONMENT=dev
API_KEY=<API key>
```

On **staging** or **production**, set the following environment variable ```ENVIRONMENT=`staging` or `production` ```
and provide the API key via the URL arguments. For example: `http://localhost:5006/correlation?api_key=valid_key` 

To install a branch during development, edit the `master` with the branch name.
This will work for both options above.

## Changes and Version Number
With every PR merged into the `master` branch, please add a version tag to the latest commit
and add a __short__ description of the changes to the file `CHANGES.md` (newer entries at the top).