import pathlib

from setuptools import setup

# The directory containing this file
root_directory = pathlib.Path(__file__).parent

# The text of the README file
readme = (root_directory / "README.md").read_text(encoding="UTF-8")

# This call to setup() does all the work
setup(
    name="python-qlient",
    version="1.1.0",
    description="A fast and modern graphql client library designed with simplicity in mind.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Lab9/python-qlient",
    author="Daniel Seifert",
    author_email="info@danielseifert.ch",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Framework :: AsyncIO",
        "Natural Language :: English",
    ],
    keywords="python graphql client api async asyncio graph requests query mutation subscription",
    packages=[
        "qlient"
    ],
    include_package_data=True,
    install_requires=[
        "requests==2.*",
        "websockets==8.1"
    ],
    entry_points={
        "console_scripts": [
            "qlient=qlient.cli:main"
        ]
    },
)
