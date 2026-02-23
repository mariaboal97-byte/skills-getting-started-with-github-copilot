import copy
import pytest
from fastapi.testclient import TestClient

from src import app as application

# we copy the activities map before each test and restore it afterwards
def pytest_runtest_setup(item):
    # make sure application.activities is reset before each test
    item._original_activities = copy.deepcopy(application.activities)


def pytest_runtest_teardown(item, nextitem):
    if hasattr(item, "_original_activities"):
        application.activities = item._original_activities


client = TestClient(application.app)


def test_get_activities():
    # Arrange: nothing special to setup beyond global state

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    # should be a dictionary containing at least one known club
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    payload = {"email": "newstudent@mergington.edu"}

    # Act
    response = client.post("/activities/Chess Club/signup", params=payload)

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")
    assert "newstudent@mergington.edu" in application.activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity():
    # Arrange
    payload = {"email": "foo@bar.com"}

    # Act
    response = client.post("/activities/Nonexistent/signup", params=payload)

    # Assert
    assert response.status_code == 404


def test_signup_duplicate():
    # Arrange
    existing = application.activities["Chess Club"]["participants"][0]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": existing})

    # Assert
    assert response.status_code == 400


def test_remove_participant_success():
    # Arrange
    participant = application.activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": participant})

    # Assert
    assert response.status_code == 200
    assert participant not in application.activities["Chess Club"]["participants"]


def test_remove_participant_not_registered():
    # Arrange: choose email not registered
    email = "nobody@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_remove_nonexistent_activity():
    # Arrange
    email = "foo@bar.com"

    # Act
    response = client.delete("/activities/NotAThing/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
