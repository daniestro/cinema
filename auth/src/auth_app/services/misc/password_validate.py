import re


def validate_password(password: str) -> bool:
    r"""Password validator.

    Require at least:
        1 special symbol: @$!%*#?&"'
        1 lowercase: a-z
        1 uppercase: A-Z
        1 digit: 0-9
    Password length: 6-50
    """
    reg = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&"\'])[A-Za-z\d@$!%*#?&"\']{6,50}$'
    pat = re.compile(reg)
    if pat.search(password):
        return True
    return False
