from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Marketplace Campaign Rules"
