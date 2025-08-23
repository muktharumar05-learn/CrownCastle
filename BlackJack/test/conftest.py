import pytest
from core.client import APIClient

@pytest.fixture(scope="session")
def client():
    return APIClient()
