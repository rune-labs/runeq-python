# runeq-python

![PyPI - License](https://img.shields.io/pypi/l/runeq)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/runeq)
![PyPI](https://img.shields.io/pypi/v/runeq)
[![Documentation Status](https://readthedocs.org/projects/runeq/badge/?version=latest)](https://runeq.readthedocs.io/en/latest/?badge=latest)
[![CircleCI Status](https://circleci.com/gh/rune-labs/runeq-python.svg?style=shield)](https://app.circleci.com/pipelines/gh/rune-labs/runeq-python)

Python 3 Standard Development Kit (SDK) for Rune Lab's Query API: `runeq`

## References

* Library documentation: [https://runeq.readthedocs.io/en/latest](https://runeq.readthedocs.io/en/latest)
* API documentation: [https://docs.runelabs.io](https://docs.runelabs.io)
* Rune Labs home page: [https://runelabs.io](https://runelabs.io)

## Installation

Python 3.8+ is required.

To install the library using pip:

    pip3 install runeq

To install from source:

    python3 setup.py install

## Development

Initialize a virtual environment, with dev requirements installed:

    make init

### Run tests
    
    make test
    # With coverage
    make test-coverage
    # For a single test
    make test-single


### Lint

    make lint

### Preview documentation
    
    make build-docs

- This will build the documents in the `docs` directory. Open the `index.html` file in your browser to preview the documentation.

### Build PyPI artifact:

    make build-dist

### Clean up ignored files/artifacts

    make clean
