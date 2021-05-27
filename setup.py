from setuptools import setup, find_packages

setup(
    name="mz_bokeh_package",
    version="0.0.3",
    packages=find_packages(),

    # Requirements for the package.
    install_requires=[
        "requests",
        "bokeh",
    ],
    extras_require={
        "development": [
            "flake8~=3.8",
        ],
    },

    # PyPI metadata.
    author="Ori Yudilevich",
    author_email="ori@materials.zone",
    description="Common functionality for creating apps on the MaterialsZone platform.",
    keywords="",
    url="www.materials.zone",
    project_urls={
        "Source Code": "https://github.com/materialscloud/mz-bokeh-package",
    },

    # TODO: Add some stuff about licensing.
    classifiiers=[]
)
