"""
Tests for the High School Management System API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in regional tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and participate in swim meets",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["sarah@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 30,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through competitive debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_html(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Swimming Club" in data
    
    def test_get_activities_structure(self, client):
        """Test that activity structure is correct"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post("/activities/Swimming%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Swimming Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Swimming Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        # First signup
        client.post("/activities/Swimming%20Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Swimming%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post("/activities/Nonexistent%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_activity_with_space(self, client):
        """Test signing up for activity with spaces in name"""
        response = client.post("/activities/Chess%20Club/signup?email=newchess@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newchess@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who is not signed up"""
        response = client.delete("/activities/Chess%20Club/unregister?email=noone@mergington.edu")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete("/activities/Nonexistent%20Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_and_signup_again(self, client):
        """Test that a participant can unregister and sign up again"""
        # Unregister
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Sign up again
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant is back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for common user scenarios"""
    
    def test_full_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and unregistering"""
        email = "integration@mergington.edu"
        activity = "Drama Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify participant was added
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify participant was removed
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert len(after_unregister_data[activity]["participants"]) == initial_count
        assert email not in after_unregister_data[activity]["participants"]
    
    def test_multiple_participants_signup(self, client):
        """Test multiple participants signing up for the same activity"""
        activity = "Swimming Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data[activity]["participants"]
