import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def create_directory_for_images(request) -> None:
    dir_name = "test_results"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)


@pytest.fixture(scope="session")
def display_window(request) -> bool:
    return request.config.option.display_window


def pytest_addoption(parser):
    parser.addoption("--display_window", action="store_true", default=False)
