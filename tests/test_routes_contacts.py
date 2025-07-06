import json
import pytest
from fastapi.testclient import TestClient
from src.auth.auth import create_access_token
from main import app

contact_data = {
    "first_name": "Wade",
    "last_name": "Wilson",
    "email": "wade@example.com",
    "phone_number": "+1234567890",
    "birthday": "1991-01-01"
}


client = TestClient(app)

@pytest.mark.asyncio
async def test_create_contact(client, get_token):
    headers = {
        "Authorization": f"Bearer {get_token}"
    }

    response = client.post(
        "/contacts/",
        headers=headers,
        json=contact_data
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == contact_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_read_all_contacts(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)



@pytest.mark.asyncio
async def test_search_contact(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/search?email=wade@example.com", headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert result[0]["email"] == contact_data["email"]


@pytest.mark.asyncio
async def test_read_contact_by_id(get_token, existing_contact_id, async_client):
    token = await get_token
    contact_id = existing_contact_id

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"/contacts/{contact_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id



@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/upcoming-birthdays", headers=headers)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_update_contact(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    updated_data = contact_data.copy()
    updated_data["first_name"] = "Updated"
    response = client.put("/contacts/7", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_contact(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.delete("/contacts/7", headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_deleted_contact_by_id(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/7", headers=headers)
    assert response.status_code == 404