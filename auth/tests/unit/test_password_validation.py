from auth_app.services.misc import validate_password


def test_strong_password():
    assert validate_password('@Gopaaa1"')


def test_weak_password():
    assert not validate_password("1234")
