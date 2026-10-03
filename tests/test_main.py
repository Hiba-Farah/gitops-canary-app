import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_root_contains_version():
    response = client.get("/")
    assert "V1" in response.text or "V2" in response.text or "V3" in response.text


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
