import pytest
from flask import Flask
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that the index page loads correctly and contains the button."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Click me!" in response.data
    assert b"Datadog RUM" in response.data  # Check if the RUM script is present

def test_button_click(client):
    """Test that clicking the button triggers the correct response and spans."""
    response = client.post('/click')
    assert response.status_code == 200
    assert b"Button clicked! Processing done." in response.data

