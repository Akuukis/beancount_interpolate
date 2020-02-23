init:
	pip3 install -r requirements.txt

test:
	pytest

upload:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: init test
