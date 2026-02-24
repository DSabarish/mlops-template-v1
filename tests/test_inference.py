"""Test inference API: predict returns float."""
import os
import joblib
import tempfile
from sklearn.linear_model import LinearRegression
import numpy as np

# Create a minimal model so /predict can load without GCS
def _make_fake_model():
    m = LinearRegression()
    m.fit(np.ones((2, 5)), np.array([1.0, 2.0]))
    return m


import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _mock_model(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        joblib.dump(_make_fake_model(), f.name)
        monkeypatch.setenv("MODEL_PATH", f.name)
    import inference
    inference._model = None
    yield
    try:
        os.unlink(f.name)
    except Exception:
        pass


from inference import app
client = TestClient(app)


def test_predict_returns_float():
    """POST /predict with valid body returns prediction as float."""
    resp = client.post(
        "/predict",
        json={"f1": 1.0, "f2": 2.0, "f3": 3.0, "f4": 4.0, "f5": 5.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], (int, float))


def test_health_ok():
    """GET /health returns 200."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
