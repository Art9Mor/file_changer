import pytest


@pytest.mark.asyncio
async def test_list_files_empty(client, api_headers):
    response = await client.get('/files', headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['items'] == []
    assert body['total'] == 0
    assert body['skip'] == 0
    assert body['limit'] == 20


@pytest.mark.asyncio
async def test_list_files_pagination_params(client, api_headers):
    response = await client.get('/files', params={'skip': 5, 'limit': 10}, headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['skip'] == 5
    assert body['limit'] == 10


@pytest.mark.asyncio
async def test_list_files_reflects_upload(client, api_headers):
    await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'В каталоге'},
        files={'file': ('listed.txt', b'ok', 'text/plain')},
    )
    response = await client.get('/files', headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['title'] == 'В каталоге'
