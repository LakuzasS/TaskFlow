"""
Module de gestion des utilisateurs et de l'authentification Google pour une application TaskFlow.

Ce module fournit des fonctions pour :
- Se connecter à une base de données MySQL.
- Créer, connecter, déconnecter, et gérer des utilisateurs (y compris via Google OAuth2).
- Envoyer des e-mails de confirmation à travers l'API Gmail.

Imports:
    mysql.connector: Utilisé pour interagir avec la base de données MySQL.
    bcrypt: Utilisé pour chiffrer et vérifier les mots de passe.
    requests: Utilisé pour faire des requêtes HTTP (Google API).
    google.oauth2.id_token: Utilisé pour vérifier les tokens OAuth2 Google.
    google.auth.transport.requests: Utilisé pour transporter les requêtes Google.
    googleapiclient.discovery.build: Utilisé pour interagir avec l'API Gmail de Google.
    email.mime.text.MIMEText: Utilisé pour formater les e-mails envoyés via Gmail.

Variables:
    SCOPES (list): Liste des autorisations nécessaires pour interagir avec l'API Gmail.
    CLIENT_ID (str): ID client Google OAuth2.
"""

import sys
import os

from backend.db_api import DB_API

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

from backend.config import CLIENT_ID, SCOPES


def login_with_google(id_token_str):
    idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), CLIENT_ID)
    email = idinfo.get("email")
    google_name = idinfo.get("name")

    result = DB_API.get_all_infos_from_email(email)
    if isinstance(result, Exception):
        print(result)
        return False

    if result:
        return True
    else:
        create_user_google(google_name, email)
        return True


def create_user_google(username, email):
    """
    Crée un utilisateur Google dans la base de données.

    Args:
        username (str): Le nom d'utilisateur de Google.
        email (str): L'adresse e-mail de l'utilisateur Google.

    Returns:
        None
    """
    DB_API.add_user(username, "", email, 1)
    send_confirmation_email(email, username)


def send_confirmation_email(to_email, username):
    """
    Envoie un e-mail de confirmation à l'utilisateur après la création de son compte.

    Args:
        to_email (str): L'adresse e-mail de l'utilisateur.
        username (str): Le nom d'utilisateur de l'utilisateur.

    Returns:
        None
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../api/credentials.json")
            )
            flow = InstalledAppFlow.from_client_secrets_file(file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    message = MIMEText(
        f"Bonjour {username},\n\nVotre compte a été créé avec succès."
        f"\nMerci de vous être inscrit sur TaskFlow !"
    )
    message["to"] = to_email
    message["subject"] = "Confirmation de création de compte"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service = build("gmail", "v1", credentials=creds)
    try:
        message = {"raw": raw_message}
        service.users().messages().send(userId="me", body=message).execute()
    except Exception:
        pass
