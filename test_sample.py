import pytest
from unittest.mock import patch

@pytest.fixture
def client():
    # Parcheamos in_bd para que no intente conectar a MySQL al importar sample_app
    with patch('sample_app.in_bd'):
        from sample_app import sample
        sample.config['TESTING'] = True
        with sample.test_client() as client:
            yield client

def test_home_status_code(client):
    with patch('pymysql.connect') as mock_connect:
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        response = client.get('/')
        assert response.status_code == 404