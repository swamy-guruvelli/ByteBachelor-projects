import os
from pathlib import Path

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./task_api_test.db",
)

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()
    Path("task_api_test.db").unlink(missing_ok=True)


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
