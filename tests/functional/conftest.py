import sys
import pytest
from pathlib import Path
from multiprocessing import Queue


mypath = Path(__file__)
sys.path.insert(0, str(mypath.parents[2].resolve().absolute()))
from src.server import app


@pytest.fixture
def client():
    app.shared_ctx.logger_queue = Queue()
    yield app.asgi_client
