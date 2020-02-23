init:
    pip install -r requirements.txt

test:
    pytest

.PHONY: init test
