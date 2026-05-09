import pytest


@pytest.mark.asyncio
async def test_list_alerts_empty(client, api_headers):
    response = await client.get('/alerts', headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['items'] == []
    assert body['total'] == 0


@pytest.mark.asyncio
async def test_list_alerts_pagination_reflects_params(client, api_headers):
    response = await client.get('/alerts', params={'skip': 2, 'limit': 5}, headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['skip'] == 2
    assert body['limit'] == 5
