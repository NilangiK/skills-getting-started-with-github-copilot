import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=True)


def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=test1@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test1@mergington.edu for Chess Club" in data["message"]

    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "test1@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client):
    response = client.post("/activities/Nonexistent/signup?email=test2@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate(client):
    # First signup
    client.post("/activities/Programming Class/signup?email=test3@mergington.edu")
    # Duplicate
    response = client.post("/activities/Programming Class/signup?email=test3@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_success(client):
    # First signup
    client.post("/activities/Gym Class/signup?email=test4@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Gym Class/unregister?email=test4@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered test4@mergington.edu from Gym Class" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "test4@mergington.edu" not in data["Gym Class"]["participants"]


def test_unregister_nonexistent_activity(client):
    response = client.delete("/activities/Nonexistent/unregister?email=test5@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Soccer Team/unregister?email=test6@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not signed up for this activity"