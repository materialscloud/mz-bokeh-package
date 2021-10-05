from setuptools import setup

setup(
    name="mz_bokeh_package",
    version="0.5.1",
    packages=["mz_bokeh_package"],
    include_package_data=True,

    # Requirements for the package.
    install_requires=[
        "requests",
        "bokeh~=2.3.0",
    ],
    extras_require={
        "development": [
            "flake8~=3.8",
            "pytest~=6.2.4",
        ],
    },

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
