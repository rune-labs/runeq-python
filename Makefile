VENV_NAME := venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate

.PHONY: clean
clean:
	rm -rf build/ dist/ runeq.egg-info/
	# clean up test/coverage artifacts
	rm -rf .coverage coverage.xml test-reports/ htmlcov/
	# clean up docs
	make -C docs clean

$(VENV_NAME):
	# Set up virtual environment
	python3 -m venv --prompt $(shell basename `pwd`) venv
	. $(VENV_ACTIVATE) && pip install --upgrade pip

.PHONY: init
init: $(VENV_NAME)
	# Set up a virtual environment with dev requirements
	. $(VENV_ACTIVATE) && pip install -r requirements/dev.txt

.PHONY: lint
lint:
	. $(VENV_ACTIVATE) && flake8 .

.PHONY: test
test:
	# Run test suite
	. $(VENV_ACTIVATE) && python3 -m unittest -v -k tests

.PHONY: test-coverage
test-coverage:
	# Run tests wth coverage report
	. $(VENV_ACTIVATE) && coverage run --source runeq -m xmlrunner discover -v -s tests -p '*.py' -o test-reports
	. $(VENV_ACTIVATE) && coverage report
	. $(VENV_ACTIVATE) && coverage html
	. $(VENV_ACTIVATE) && coverage xml

.PHONY: build-docs
build-docs:
	# Build docs (as HTML)
	. $(VENV_ACTIVATE) && make -C docs html

.PHONY: build-pypi
build-pypi:
	# Build artifact for PyPI
	. $(VENV_ACTIVATE) && TODO
