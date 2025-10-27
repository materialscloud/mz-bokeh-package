from setuptools import setup

setup(
    name="mz_bokeh_package",
    version="0.20.0",
    packages=["mz_bokeh_package"],
    include_package_data=True,

    # Requirements for the package.
    install_requires=[
        "bokeh~=3.8.0",
        "numpy~=2.3.4",
        "seaborn~=0.13.2",
        "gql[requests]~=4.0.0",
        "jsonschema~=4.25.1",
    ],
    extras_require={
        "development": [
            "flake8~=7.3.0",
            "pytest~=8.4.2",
        ],
    },
    python_requires=">=3.12,<3.13",

    # PyPI metadata.
    author="Ori Yudilevich <ori@materials.zone>, \
        Roi Weinreb <roi.weinreb@materials.zone>",
    description="Common functionality for creating apps on the MaterialsZone platform.",
    keywords="",
    url="www.materials.zone",
    project_urls={
        "Source Code": "https://github.com/materialscloud/mz-bokeh-package",
    },

    # TODO: Add some stuff about licensing.
    classifiers=[]
)
