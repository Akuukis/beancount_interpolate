install:
	python3 -m venv .venv
	. .venv/bin/activate; pip3 install -r requirements.txt --upgrade
	printf '\nrun:\n    source .venv/bin/activate\n\n'

try:
	pip3 install .

test:
	pytest --maxfail=1 -v

clean:
	rm -rf build dist beancount_interpolate.egg-info/

build: clean
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

.PHONY: install test
