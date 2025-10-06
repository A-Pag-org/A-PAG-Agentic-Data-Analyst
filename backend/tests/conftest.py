import os
import sys
from typing import Generator

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure backend package importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("APP_AUTOINIT", "0")  # prevent module-level app creation
os.environ.setdefault("APP_MINIMAL", "1")   # prefer minimal router in tests
from app.main import create_app  # noqa: E402


@pytest.fixture()
def anyio_backend() -> str:
    # Ensure httpx AsyncClient uses asyncio backend
    return "asyncio"


@pytest.fixture()
def test_client() -> Generator[TestClient, None, None]:
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("APP_MINIMAL", "1")
    app: FastAPI = create_app(minimal=True)
    with TestClient(app) as client:
        yield client
