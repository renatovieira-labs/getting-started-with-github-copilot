"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
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
        "Basketball Team": {
            "description": "Join the basketball team and compete in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates and improve public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Club": {
            "description": "Solve challenging math problems and participate in competitions",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 15,
            "participants": []
        }
    }
    
    # Clear existing activities
    activities.clear()
    
    # Restore original state
    for key, value in original_activities.items():
        activities[key] = {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
    
    yield


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
    
    def test_get_activities_returns_activity_details(self, client):
        """Test that activities contain correct details"""
        response = client.get("/activities")
        activities_data = response.json()
        chess_club = activities_data["Chess Club"]
        
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
    
    def test_get_activities_returns_participants(self, client):
        """Test that activities return participant lists"""
        response = client.get("/activities")
        activities_data = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities_data["Chess Club"]["participants"]) == 2
        # Basketball Team should have 0 participants
        assert len(activities_data["Basketball Team"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "student@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        # Signup
        client.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        activities_data = response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up with duplicate email returns 400"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_multiple_signups_increase_participant_count(self, client):
        """Test that multiple signups are added correctly"""
        # Sign up two different students
        client.post("/activities/Basketball%20Team/signup?email=student1@mergington.edu")
        client.post("/activities/Basketball%20Team/signup?email=student2@mergington.edu")
        
        # Verify both are added
        response = client.get("/activities")
        participants = response.json()["Basketball Team"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 2


class TestRemoveParticipant:
    """Tests for the POST /activities/{activity_name}/remove endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        response = client.post(
            "/activities/Chess%20Club/remove?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_remove_actually_removes_participant(self, client):
        """Test that removal actually removes the participant"""
        # Verify participant exists
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]
        
        # Remove participant
        client.post("/activities/Chess%20Club/remove?email=michael@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]
    
    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that removing from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/remove?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant_returns_400(self, client):
        """Test that removing nonexistent participant returns 400"""
        response = client.post(
            "/activities/Basketball%20Team/remove?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestActivityCapacity:
    """Tests for activity capacity management"""
    
    def test_activity_respects_max_participants(self, client):
        """Test that activities can reach max capacity"""
        # Get Art Club which has max 10 participants
        response = client.get("/activities")
        art_club = response.json()["Art Club"]
        
        # Art Club starts with 0 participants and max of 10
        assert len(art_club["participants"]) == 0
        assert art_club["max_participants"] == 10
    
    def test_spots_left_calculation(self, client):
        """Test that spots left are calculated correctly"""
        response = client.get("/activities")
        activities_data = response.json()
        
        # Basketball Team: max 15, 0 participants = 15 spots left
        basketball = activities_data["Basketball Team"]
        spots_left = basketball["max_participants"] - len(basketball["participants"])
        assert spots_left == 15
        
        # Chess Club: max 12, 2 participants = 10 spots left
        chess = activities_data["Chess Club"]
        spots_left = chess["max_participants"] - len(chess["participants"])
        assert spots_left == 10
