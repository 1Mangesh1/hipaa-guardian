# pytest Advanced Patterns

## Async Testing

```python
import pytest

# Requires: pip install pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data()
    assert result == expected

# Async fixture
@pytest.fixture
async def async_client():
    async with AsyncClient(app) as client:
        yield client

@pytest.mark.asyncio
async def test_api(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

## Factory Fixtures

```python
@pytest.fixture
def make_user():
    """Factory fixture for creating users."""
    created = []

    def _make_user(name="Test", email=None, role="user"):
        email = email or f"{name.lower()}@test.com"
        user = User(name=name, email=email, role=role)
        db.add(user)
        created.append(user)
        return user

    yield _make_user

    for user in created:
        db.delete(user)

def test_admin_permissions(make_user):
    admin = make_user("Admin", role="admin")
    regular = make_user("User", role="user")
    assert admin.can_delete(regular)
```

## Fixture Composition

```python
@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(db):
    Session = sessionmaker(bind=db)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user(session):
    user = User(name="Alice", email="alice@test.com")
    session.add(user)
    session.commit()
    return user
```

## Custom Markers

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks slow tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")

# Run specific markers
# pytest -m slow
# pytest -m "not slow"
# pytest -m "integration or e2e"
```

## Monkeypatch

```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert os.environ["API_KEY"] == "test-key"

def test_modify_dict(monkeypatch):
    monkeypatch.setitem(app.config, "DEBUG", True)

def test_remove_attr(monkeypatch):
    monkeypatch.delattr("os.path.exists")

def test_change_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
```

## tmp_path Fixture

```python
def test_file_operations(tmp_path):
    # tmp_path is a pathlib.Path to a temp directory
    file = tmp_path / "test.txt"
    file.write_text("hello")
    assert file.read_text() == "hello"

def test_with_config(tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"debug": true}')
    app = App(config_path=str(config))
    assert app.debug is True
```

## Useful Plugins

```
pytest-cov        # Coverage reporting
pytest-mock       # mocker fixture
pytest-asyncio    # Async test support
pytest-xdist      # Parallel test execution
pytest-randomly   # Randomize test order
pytest-timeout    # Test timeouts
pytest-benchmark  # Performance benchmarking
pytest-freezegun  # Time freezing
pytest-factoryboy # Factory fixtures
pytest-httpx      # Mock httpx requests
pytest-django     # Django integration
```

## Django Testing

```python
import pytest
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create(username="alice")
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_api_endpoint(client):
    response = client.get("/api/users/")
    assert response.status_code == 200
```

## FastAPI Testing

```python
import pytest
from fastapi.testclient import TestClient
from myapp import app

@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}

def test_create_item(client):
    response = client.post("/items/", json={"name": "Foo", "price": 42.0})
    assert response.status_code == 201
```
