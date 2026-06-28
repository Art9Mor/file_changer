import pytest

from src.domain.constants import MAX_UPLOAD_BYTES


@pytest.mark.asyncio
async def test_upload_file_success(client, api_headers):
    response = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Документ'},
        files={'file': ('hello.txt', b'hello world', 'text/plain')},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload['title'] == 'Документ'
    assert payload['original_name'] == 'hello.txt'
    assert payload['mime_type'] == 'text/plain'
    assert payload['size'] == 11
    assert payload['processing_status'] == 'uploaded'


@pytest.mark.asyncio
async def test_upload_rejects_empty_file(client, api_headers):
    response = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Пустой'},
        files={'file': ('empty.txt', b'', 'text/plain')},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client, api_headers):
    big = b'x' * (MAX_UPLOAD_BYTES + 1)
    response = await client.post(
        '/files',
        headers=api_headers,
        data={'title': 'Большой'},
        files={'file': ('big.bin', big, 'application/octet-stream')},
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_upload_forbidden_without_key(client):
    response = await client.post(
        '/files',
        data={'title': 'X'},
        files={'file': ('a.txt', b'a', 'text/plain')},
    )
    assert response.status_code == 403