import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_homepage():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/homepage")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "featured_products" in data["data"]
    assert "promotions" in data["data"]
    assert "faqs" in data["data"]
