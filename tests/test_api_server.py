import pytest
from httpx import AsyncClient, ASGITransport
from src.api_server import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_webhook_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/webhook", json={"service": "test", "event_type": "alert"})
        assert resp.status_code in (200, 202)

@pytest.mark.asyncio
async def test_hec_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/hec", json={"event": "test"})
        assert resp.status_code in (200, 202)
