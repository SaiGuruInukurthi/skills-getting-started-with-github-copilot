from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure the test email is not present to start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup (use quoted activity name)
    signup_path = f"/activities/{quote(activity)}/signup"
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    delete_path = f"/activities/{quote(activity)}/participants"
    resp = client.delete(delete_path, params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
import copy
import urllib.parse
import pytest

from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of the activities and restore after each test
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = orig


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Sign up
    signup_resp = client.post(
        f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    )
    assert signup_resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Ensure participant shows in GET
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    assert email in get_resp.json()[activity]["participants"]

    # Duplicate signup should return 400
    dup_resp = client.post(
        f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    )
    assert dup_resp.status_code == 400

    # Unregister
    del_resp = client.delete(
        f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}"
    )
    assert del_resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering again should return 404
    del_resp2 = client.delete(
        f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}"
    )
    assert del_resp2.status_code == 404
