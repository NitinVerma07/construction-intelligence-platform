import os
import tempfile

# Must be set before the app is imported: force offline mode and an isolated database.
os.environ["LLM_MODE"] = "mock"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
