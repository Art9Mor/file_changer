import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.asyncio
async def test_files_forbidden_without_api_key(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/files')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_files_forbidden_with_wrong_api_key(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/files', headers={'X-API-Key': 'wrong'})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_openapi_docs_served_without_api_key(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/docs')
    assert response.status_code == 200
    assert 'swagger' in response.text.lower() or 'openapi' in response.text.lower()


@pytest.mark.asyncio
async def test_openapi_docs_ok_with_api_key(app, api_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.get('/docs', headers=api_headers)
    assert response.status_code == 200
