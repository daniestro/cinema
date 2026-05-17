from secrets import choice
from string import ascii_lowercase, ascii_uppercase, digits

from faker import Faker

alphabet = ascii_lowercase + ascii_uppercase + digits + "@$!%*#?&\"'"


def generate_user() -> dict:
    faker = Faker()

    password = "".join([choice(alphabet) for _ in range(5)]) + "Aa1@"
    return {"email": faker.email(), "password": password}
