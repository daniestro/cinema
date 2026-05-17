from auth_app.services.hash_service import get_hash_service


def test_hash_service():
    hash_service = get_hash_service()
    password = "opachki"
    hashed_password = hash_service.hash(password)
    assert hash_service.verify(password, hashed_password)


def test_negative_hash_service():
    hash_service = get_hash_service()
    password = "opachki"
    hashed_password = hash_service.hash(password)
    wrond_password = "pppp"
    assert not hash_service.verify(wrond_password, hashed_password)
