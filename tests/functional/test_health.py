import pytest


@pytest.mark.asyncio
async def test_health_response(client):
    (request, response) = await client.get("/")
    assert response.json["status"] == 200
    assert "HEALTHY" in response.json["message"]
