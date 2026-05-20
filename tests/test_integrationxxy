from unittest.mock import patch, MagicMock

def test_send_password_code_integration(client):
    """
    Integration test for the /api/send-password-code endpoint.
    This tests the Flask routing, request parsing, and database interaction,
    while mocking the actual MySQL connection to avoid side effects.
    """
    # Create mock objects for the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Configure the mock connection to return our mock cursor
    mock_conn.cursor.return_value = mock_cursor
    
    # Simulate that the UPDATE query affected 1 row (user found)
    mock_cursor.rowcount = 1
    
    # Patch the get_db function used in routes/auth.py
    with patch('routes.auth.get_db', return_value=mock_conn):
        # Make a request to the endpoint
        response = client.post('/api/send-password-code', json={
            'email': 'admin@example.com'
        })
        
        # Verify the response status code and JSON data
        assert response.status_code == 200
        assert response.json == {"message": "Verification code set successfully"}
        
        # Verify that the database was queried correctly
        mock_conn.cursor.assert_called_once()
        # Verify the UPDATE query was executed
        assert mock_cursor.execute.called
        # Verify changes were committed
        assert mock_conn.commit.called
        # Verify connections were closed
        assert mock_cursor.close.called
        assert mock_conn.close.called

def test_send_password_code_user_not_found(client):
    """Test the password code endpoint when the user is not in the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Simulate that the UPDATE query affected 0 rows (user not found)
    mock_cursor.rowcount = 0
    
    with patch('routes.auth.get_db', return_value=mock_conn):
        response = client.post('/api/send-password-code', json={
            'email': 'nonexistent@example.com'
        })
        
        assert response.status_code == 404
        assert "error" in response.json
