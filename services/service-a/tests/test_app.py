import pytest
from app import app, _users, _next_id


@pytest.fixture(autouse=True)
def clear_store():
    """Reset in-memory store before every test."""
    global _next_id
    _users.clear()
    import app as m
    m._next_id = 1
    yield


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_health_returns_ok(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'ok'


def test_create_user_returns_201(client):
    res = client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    assert res.status_code == 201
    body = res.get_json()
    assert body['name']  == 'Alice'
    assert body['email'] == 'alice@example.com'
    assert 'id' in body


def test_list_users_returns_created_users(client):
    client.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
    client.post('/users', json={'name': 'Eve', 'email': 'eve@example.com'})
    res = client.get('/users')
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_user_by_id(client):
    created = client.post('/users', json={'name': 'Carol', 'email': 'carol@example.com'}).get_json()
    res = client.get(f'/users/{created["id"]}')
    assert res.status_code == 200
    assert res.get_json()['email'] == 'carol@example.com'


def test_delete_user_removes_it(client):
    created = client.post('/users', json={'name': 'Dave', 'email': 'dave@example.com'}).get_json()
    res = client.delete(f'/users/{created["id"]}')
    assert res.status_code == 200
    assert client.get(f'/users/{created["id"]}').status_code == 404
