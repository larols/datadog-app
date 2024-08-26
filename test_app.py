def test_index_page(client):
    """Test that the index page loads correctly and contains the button."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Click me!" in response.data  # Check if the button is present

