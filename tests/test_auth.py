import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from api.api_google import app
from backend.config import CLIENT_ID
import logging
from backend.auth import login_with_google, create_user_google, send_confirmation_email
logging.basicConfig(level=logging.DEBUG)

# Patch les méthodes pour simuler le comportement de Google OAuth et de la base de données
@pytest.fixture
def mock_google_oauth2_token():
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock:
        yield mock


@pytest.fixture
def mock_requests_post():
    with patch("requests.post") as mock:
        yield mock


@pytest.fixture
def mock_login_with_google():
    with patch("backend.auth.login_with_google") as mock:
        yield mock


def test_oauth2callback_success(mock_google_oauth2_token, mock_requests_post, mock_login_with_google):
    # Simuler une réponse réussie de Google OAuth
    mock_google_oauth2_token.return_value = {
        "email": "test@example.com",
        "name": "Test User"
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id_token": "mock_id_token"}
    mock_requests_post.return_value = mock_response

    # Simuler un succès de la fonction login_with_google
    mock_login_with_google.return_value = True

    # Créer un client Flask pour effectuer des tests
    client = app.test_client()

    # Effectuer la requête GET pour la route /oauth2callback avec un code simulé
    response = client.get("/oauth2callback?code=mock_code")
    data = response.data.decode()

    # Vérifier que la requête s'est bien terminée avec un code 200
    assert response.status_code == 200
    assert "Connexion à Test User réussie" in data  # Message personnalisé de succès

    # Vérifier que la méthode 'verify_oauth2_token' a été appelée une seule fois
    mock_requests_post.assert_called_once()
    assert mock_google_oauth2_token.call_count == 1


def test_oauth2callback_missing_code(mock_google_oauth2_token, mock_requests_post):
    # Créer un client Flask pour effectuer des tests
    client = app.test_client()

    # Effectuer la requête GET pour la route /oauth2callback sans code
    response = client.get("/oauth2callback")
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data["message"] == "Code manquant."


def test_oauth2callback_token_error(mock_google_oauth2_token, mock_requests_post):
    # Simuler une réponse réussie de Google OAuth mais avec un ID token manquant
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_requests_post.return_value = mock_response

    client = app.test_client()

    # Effectuer la requête GET pour la route /oauth2callback avec un code simulé
    response = client.get("/oauth2callback?code=mock_code")
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data["message"] == "Token ID manquant."


def test_google_login_success(mock_login_with_google):
    # Simuler une réponse réussie de login_with_google
    mock_login_with_google.return_value = True

    client = app.test_client()

    # Simuler une requête POST à /api/login/google avec un token valide
    response = client.post(
        "/api/login/google",
        data=json.dumps({"id_token": "mock_valid_id_token"}),
        content_type="application/json"
    )

    # Vérifier si le serveur a renvoyé une erreur HTML (500)
    if response.content_type != "application/json":
        print(f"Unexpected response content: {response.data.decode()}")

    try:
        # Décoder la réponse JSON
        data = json.loads(response.data)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON. Response data: {response.data.decode()}")
        raise e

    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "Connexion réussie."


def test_google_login_missing_token(mock_login_with_google):
    # Simuler une requête POST à /api/login/google sans id_token
    client = app.test_client()

    response = client.post(
        "/api/login/google",
        data=json.dumps({}),
        content_type="application/json"
    )
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data["message"] == "Token ID manquant."


def test_google_login_failure(mock_login_with_google):
    # Simuler une réponse échouée de login_with_google
    mock_login_with_google.return_value = False

    client = app.test_client()

    # Simuler une requête POST à /api/login/google avec un token invalide
    response = client.post(
        "/api/login/google",
        data=json.dumps({"id_token": "mock_invalid_id_token"}),
        content_type="application/json"
    )

    # Vérifier si le serveur a renvoyé une erreur HTML (500)
    if response.content_type != "application/json":
        print(f"Unexpected response content: {response.data.decode()}")

    try:
        # Décoder la réponse JSON
        data = json.loads(response.data)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON. Response data: {response.data.decode()}")
        raise e

    assert response.status_code == 401
    assert data["success"] is False
    assert data["message"] == "Échec de la connexion."


@patch("backend.auth.id_token.verify_oauth2_token")
@patch("backend.auth.DB_API.get_all_infos_from_email")
def test_login_with_google_existing_user(mock_get_info, mock_verify):
    mock_verify.return_value = {"email": "test@example.com", "name": "Test User"}
    mock_get_info.return_value = {"id": 1, "email": "test@example.com"}

    result = login_with_google("mock_id_token")
    assert result is True


@patch("backend.auth.DB_API.add_user")
@patch("backend.auth.send_confirmation_email")
def test_create_user_google(mock_send_email, mock_add_user):
    create_user_google("Test User", "test@example.com")
    mock_add_user.assert_called_once_with("Test User", "", "test@example.com", 1)
    mock_send_email.assert_called_once_with("test@example.com", "Test User")


@patch("googleapiclient.discovery.build")
@patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
def test_send_confirmation_email(mock_credentials, mock_gmail_build):
    # Simule les credentials OAuth
    mock_creds = MagicMock()
    mock_credentials.return_value = mock_creds

    # Simule le service Gmail
    mock_service = MagicMock()
    mock_send = MagicMock()

    # Nous simulons la réponse de la méthode execute
    mock_send.return_value = {"status": "sent"}
    mock_service.users().messages().send.return_value.execute = mock_send
    mock_gmail_build.return_value = mock_service

    # Appel de la fonction que vous testez
    send_confirmation_email("test@example.com", "Test User")

    # Vérifiez que la méthode execute() a bien été appelée une seule fois
    # Si le test échoue à cet endroit, cela veut dire que `execute` n'a pas été invoquée
    mock_send.assert_called_once()

    # Vérifiez que la méthode send() a bien été appelée avec les bons arguments
    args, kwargs = mock_service.users().messages().send.call_args
    assert args[0]["userId"] == "me"  # Cela assure que l'utilisateur 'me' est bien passé en argument
    assert "raw" in args[0]["body"]  # Cela assure que le corps du message contient un message encodé en base64

    # Vérifiez également que le fichier de credentials est chargé
    mock_credentials.assert_called_once_with("token.json", ["your_scopes_here"])

if __name__ == "__main__":
    pytest.main()