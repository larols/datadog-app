import pytest
from app import app  # Import your Flask app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that the index page loads correctly and contains the button."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Click me!" in response.data  # Check if the button is present

