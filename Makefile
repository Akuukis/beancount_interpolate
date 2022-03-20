install:
	pip3 install -r requirements.txt --upgrade

try:
	pip3 install .

test:
	pytest --maxfail=1 -v --cov=beancount_interpolate

clean:
	rm -rf build dist beancount_interpolate.egg-info/

build: clean
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

.PHONY: install test
