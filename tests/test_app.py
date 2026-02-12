import pytest
from fastapi.testclient import TestClient


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Basketball Club" in activities
    assert "Tennis Team" in activities


def test_get_activities_structure(client):
    """Test that activities have correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity in activities.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_signup_for_activity(client):
    """Test signing up a student for an activity"""
    email = "test@mergington.edu"
    activity = "Basketball Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_duplicate_prevention(client):
    """Test that students cannot sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    activity = "Basketball Club"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_invalid_activity(client):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity"""
    email = "unregister@mergington.edu"
    activity = "Tennis Team"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Then unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    assert email in unregister_response.json()["message"]
    
    # Verify they're no longer in participants
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity]["participants"]
    assert email not in participants


def test_unregister_not_signed_up(client):
    """Test unregistering a student who wasn't signed up"""
    email = "notregistered@mergington.edu"
    activity = "Drama Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_invalid_activity(client):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_participants_list_updated(client):
    """Test that participants list is updated after signup"""
    email = "listtest@mergington.edu"
    activity = "Art Studio"
    
    # Get initial participants count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Sign up
    client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Check updated participants count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity]["participants"])
    
    assert updated_count == initial_count + 1
    assert email in updated_response.json()[activity]["participants"]


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
