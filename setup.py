from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, "README.rst"), "r") as f:
    long_description = f.read()

setup(
    name="fro",
    version="1.1.0",
    description="A module for parsing string representations of objects",
    long_description=long_description,
    url="https://github.com/ethantkoenig/fro",
    author="Ethan Koenig",
    author_email="ethantkoenig@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords="fro parsing object representations",
    packages=find_packages(),
    install_requires=["future"]
)
