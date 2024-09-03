import pytest
import random
from app import app  # Import your Flask app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("run", range(10))  # Run the test 10 times
def test_index_page(client, run):
    """Run the test multiple times to simulate flaky behavior."""
    # Simulate a 20% chance of failure
    if random.random() < 0.2:
        raise Exception(f"Random test failure on run {run}!")

    response = client.get('/')
    assert response.status_code == 200
    assert b"Click me!" in response.data  # Check if the button is present
