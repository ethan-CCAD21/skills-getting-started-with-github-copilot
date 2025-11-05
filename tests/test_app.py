from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities_contains_expected_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic expectations
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure clean state: remove if already present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        del_resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
        assert del_resp.status_code in (200, 404)

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should be rejected
    dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup.status_code == 400

    # Unregister
    un = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert un.status_code == 200
    assert "Unregistered" in un.json().get("message", "")

    # Ensure removed
    resp2 = client.get("/activities")
    assert email not in resp2.json()[activity]["participants"]

    # Unregistering again should return 404
    not_found = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert not_found.status_code == 404


def test_nonexistent_activity_returns_404():
    r = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert r.status_code == 404