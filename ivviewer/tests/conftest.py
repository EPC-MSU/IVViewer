import pytest


def pytest_addoption(parser):
    parser.addoption("--display_window", action="store_true", default=False)


@pytest.fixture(scope="session")
def display_window(request) -> bool:
    return request.config.option.display_window
