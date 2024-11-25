import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming the FastAPI app is in 'app.main'

@pytest.mark.asyncio
async def test_homepage():
    from httpx import AsyncClient
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
