import base64
import json
import os
import secrets
import string
import urllib.request
from dotenv import load_dotenv

import dashboard.models as dashboard_models

def generate_random_id(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(characters) for _ in range(length))
    return username


def generate_random_username(length=8):
    characters = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(characters) for _ in range(length))
    return username


def generate_random_password(length=12):
    if length < 4:
        raise ValueError("Password length should be at least 4 characters to ensure complexity")

    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def generate_controller_credentials():
    pass
















