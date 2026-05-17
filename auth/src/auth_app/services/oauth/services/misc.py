import secrets
from string import ascii_lowercase, ascii_uppercase, digits


def generate_password(length: int) -> str:
    alphabet = ascii_lowercase + ascii_uppercase + digits + "@$!%*#?&\"'"
    c = secrets.choice
    password = "".join([c(alphabet) for _ in range(length)])

    return password
