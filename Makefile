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
lint: black-check isort-check flake8

.PHONY: flake8
flake8:
	. $(VENV_ACTIVATE) && flake8 .

.PHONY: black-check
black-check:
	. $(VENV_ACTIVATE) && black --check .

.PHONY: black-format
black-format:
	. $(VENV_ACTIVATE) && black .

.PHONY: isort-check
isort-check:
	. $(VENV_ACTIVATE) && isort --check .

.PHONY: isort-format
isort-format:
	. $(VENV_ACTIVATE) && isort .

.PHONY: format
format: black-format isort-format ## format code and sort imports

.PHONY: test
test:
	# Run test suite
	. $(VENV_ACTIVATE) && python3 -m unittest -v -k tests

.PHONY: test-single
test-single:
	. $(VENV_ACTIVATE) && python -m unittest -k $(TEST_NAME)

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

.PHONY: build-dist
build-dist:
	# Build artifact for PyPI
	. $(VENV_ACTIVATE) && python setup.py sdist bdist_wheel
	@echo "====================================="
	@echo "To push to PyPI, run:"
	@echo "   python3 -m twine upload dist/*"
	@echo "====================================="
