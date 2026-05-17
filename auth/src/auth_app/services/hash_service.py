from passlib.hash import pbkdf2_sha512


class HashService:
    @staticmethod
    def hash(password: str) -> str:
        return pbkdf2_sha512.hash(password)

    @classmethod
    def verify(cls, password: str, hash_: str) -> bool:
        return pbkdf2_sha512.verify(password, hash_)


def get_hash_service():
    return HashService()
