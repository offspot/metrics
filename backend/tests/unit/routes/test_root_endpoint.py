from httpx import AsyncClient

from backend.main import PREFIX


async def test_root(client: AsyncClient):
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 308
    response = await client.get("/", follow_redirects=True)
    assert str(response.url).endswith(PREFIX + "/")
    assert response.headers.get("Content-Type") == "text/html; charset=utf-8"
    assert "Swagger UI" in response.text
