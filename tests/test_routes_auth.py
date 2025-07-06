import pytest
from unittest.mock import patch, AsyncMock



def test_signup_user(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpassword",
            "role": "user"
        }
    )
    assert response.status_code == 201
    assert response.json()["Email"] == "newuser@example.com"

def test_duplicate_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "deadpool",
            "email": "deadpool@example.com",
            "password": "12345678",
            "role": "user"
        }
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "deadpool@example.com",
            "password": "12345678"
        }
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authorization"

@patch("src.routes.auth.decode_email_token", new_callable=AsyncMock)
def test_verify_email_success(mock_decode, client):
    mock_decode.return_value = "deadpool@example.com"
    response = client.get("/auth/verify-email/fake-token")
    assert response.status_code == 200
    assert response.json()["message"] == "Email successfully verified!"

@patch("src.routes.auth.decode_email_token")
def test_verify_email_invalid_token(mock_decode, client):
    mock_decode.return_value = None
    response = client.get("/auth/verify-email/invalid-token")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"

@patch("src.routes.auth.send_reset_email")
def test_request_password_reset_success(mock_send, client):
    response = client.post(
        "/auth/request-password-reset",
        params={"email": "deadpool@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Reset link sent"

def test_request_password_reset_invalid_email(client):
    response = client.post(
        "/auth/request-password-reset",
        params={"email": "unknown@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@patch("src.routes.auth.verify_password_reset_token")
def test_reset_password_success(mock_verify, client):
    mock_verify.return_value = "deadpool@example.com"
    response = client.post(
        "/auth/reset-password",
        data={
            "token": "fake-token",
            "new_password": "newsecurepass123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

@patch("src.routes.auth.verify_password_reset_token")
def test_reset_password_invalid_token(mock_verify, client):
    mock_verify.return_value = None
    response = client.post(
        "/auth/reset-password",
        data={
            "token": "invalid-token",
            "new_password": "anypass"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"