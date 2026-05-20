def test_index_route(client):
    """Test that the index (login) page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard_route(client):
    """Test that the dashboard page loads successfully."""
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_forgot_password_route(client):
    """Test that the forgot password page loads successfully."""
    response = client.get('/forgot')
    assert response.status_code == 200

def test_add_user_route(client):
    """Test that the add user page loads successfully."""
    response = client.get('/add-user')
    assert response.status_code == 200
