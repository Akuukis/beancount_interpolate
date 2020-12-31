import pytest
def pytest_addoption(parser):
    parser.addoption("--multiPluginMode", action="store_true", default=False)
