import pytest


@pytest.mark.asyncio
async def test_get_file_by_id(client, api_headers):
    created = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Один'},
        files={'file': ('one.txt', b'data', 'text/plain')},
    )
    assert created.status_code == 201
    file_id = created.json()['id']

    response = await client.get(f'/files/{file_id}', headers=api_headers)
    assert response.status_code == 200
    assert response.json()['id'] == file_id


@pytest.mark.asyncio
async def test_get_file_404(client, api_headers):
    response = await client.get(
        '/files/00000000-0000-0000-0000-000000000000',
        headers=api_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_file_title(client, api_headers):
    created = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Старое'},
        files={'file': ('f.txt', b'x', 'text/plain')},
    )
    file_id = created.json()['id']

    response = await client.patch(
        f'/files/{file_id}',
        headers=api_headers,
        json={'title': 'Новое'},
    )
    assert response.status_code == 200
    assert response.json()['title'] == 'Новое'


@pytest.mark.asyncio
async def test_download_file(client, api_headers):
    created = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Скачать'},
        files={'file': ('payload.bin', b'\x00\x01\x02', 'application/octet-stream')},
    )
    file_id = created.json()['id']

    response = await client.get(f'/files/{file_id}/download', headers=api_headers)
    assert response.status_code == 200
    assert response.content == b'\x00\x01\x02'


@pytest.mark.asyncio
async def test_delete_file(client, api_headers):
    created = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Удалить'},
        files={'file': ('del.txt', b'z', 'text/plain')},
    )
    file_id = created.json()['id']

    response = await client.delete(f'/files/{file_id}', headers=api_headers)
    assert response.status_code == 204

    again = await client.get(f'/files/{file_id}', headers=api_headers)
    assert again.status_code == 404
