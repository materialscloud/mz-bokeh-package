# np.bool8 is being phased out in favor of np.bool_ in NumPy.
# We are silencing the deprecation warning here to avoid it showing up in the pytest summary.
# TODO: Once Bokeh library is updated, we can upgrade NumPy and remove this warning suppression.

import warnings
warnings.filterwarnings("ignore", message="`np.bool8` is a deprecated alias")
