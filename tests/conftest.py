import os
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'hangr_test')
os.environ.setdefault('FOURSQUARE_API_KEY', 'test_key')
os.environ.setdefault('GOOGLE_CLIENT_ID', 'test_client_id')

import pytest
from unittest.mock import MagicMock, patch

# Prevent real MongoDB connection before app is imported
_mongo_patcher = patch('pymongo.MongoClient', MagicMock)
_mongo_patcher.start()

from app import app as flask_app
flask_app.config['TESTING'] = True


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    patches = [
        patch('routes.usuarios.db', mock_db),
        patch('routes.parties.db', mock_db),
        patch('routes.social.db', mock_db),
        patch('routes.categorias.db', mock_db),
        patch('routes.lugares.db', mock_db),
    ]
    for p in patches:
        p.start()
    with flask_app.test_client() as c:
        yield c, mock_db
    for p in patches:
        p.stop()
