Changes in MZ-Bokeh-Package
===========================

0.12.1
******

A fix following bokeh version update: when providing a path to an icon image in CustomAction, a pathlib.Path is required instead of a string.


0.10.0
******

In the `dev` environment you can now get responses from `CurrentUser.get_api_key()` and
`CurrentUser.get_user_key()` without starting a bokeh-server. For this to work, the respective 
environment variables have to be set as usual, though. Their content can be meaningful or just a dummy, according
to the requirements. Querying an undefined variable raises a `KeyError`. 
