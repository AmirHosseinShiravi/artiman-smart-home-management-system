import secrets
import string


def generate_random_id(length=8):
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


def generate_client_certificates():
    pass
