import pytest
import random
from app import app  # Import your Flask app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@pytest.mark.timeout(120)  # Set a timeout of 2 minutes (120 seconds)
def test_index_page(client):
    """Run the same test multiple times to simulate flaky behavior."""
    for run in range(10):
        try:
            # Simulate a 20% chance of failure
            if random.random() < 0.2:
                raise Exception(f"Random test failure on run {run + 1}!")

            response = client.get('/')
            assert response.status_code == 200
            assert b"Click me!" in response.data  # Check if the button is present
            
        except Exception as e:
            pytest.fail(f"Flaky test failed on run {run + 1}: {str(e)}", pytrace=False)
