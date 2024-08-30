import pytest
from app import app, db, Url, generate_short_url
from flask_migrate import upgrade


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/test_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.drop_all()

        db.create_all()

        yield app.test_client()

def test_shorten_url(client):
    response = client.post('/shorten', json={'url': 'https://www.example.com'})
    data = response.get_json()
    assert response.status_code == 201
    assert 'long_url' in data
    assert 'short_url' in data
    assert data['long_url'] == 'https://www.example.com'
    assert len(data['short_url']) == 8 + len("https://www.tinyslice.com/")

def test_fetch_url(client):
    short_url = generate_short_url()
    new_url = Url(long_url='https://www.example.com', short_url=short_url)
    db.session.add(new_url)
    db.session.commit()

    response = client.post('/fetch', json={'url': short_url})
    data = response.get_json()
    assert response.status_code == 200
    assert 'long_url' in data
    assert 'short_url' in data
    assert data['long_url'] == 'https://www.example.com'
    assert data['short_url'] == short_url

    response = client.post('/fetch', json={'url': 'nonexistent'})
    data = response.get_json()
    assert response.status_code == 404
    assert data['detail'] == "Couldn't find any record"
