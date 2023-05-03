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

- **development** - one should set the `API_KEY` environment variable and the `ENVIRONMENT` variable to _dev_.
- **staging/production** - the API key needs to be sent via the URL as a query parameter and one needs to add the `--auth-module` flag to the bokeh serve command. One can also simulate this locally to test the authentication.
