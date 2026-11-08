import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app, security  # noqa: E402
from app.migrate import migrate  # noqa: E402
from app.seed import seed_data  # noqa: E402


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.db"
    security._login_gagal.clear()
    app = create_app("testing", {"DATABASE": str(db_path)})
    migrate(str(db_path))
    with app.app_context():
        seed_data()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def ambil_csrf(client, url="/login"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


@pytest.fixture
def login(client):
    def _login(username="admin", password="Admin#2026"):
        token = ambil_csrf(client)
        return client.post("/login", data={"username": username, "password": password, "_csrf": token})
    return _login
