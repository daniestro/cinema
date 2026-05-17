from aenum import StrEnum


class AuthEndPoint(StrEnum):
    API_V1 = "/auth/api/v1/auth"
    SIGN_UP = f"{API_V1}/signup"
    SIGN_IN = f"{API_V1}/signin"
    LOGOUT = f"{API_V1}/logout"
    REFRESH = f"{API_V1}/refresh"
    LOGIN_HISTORY = f"{API_V1}/login_history"


UserEndPoint = "/api/v1/user"


class Details(StrEnum):
    WEAK_PASSWORD = "Weak password"
    INVALID_EMAIL = "Invalid email"
    ALREADY_TAKEN_EMAIL = "Already taken email"

    INVALID_EMAIL_OR_PASSWORD = "Invalid email or password"
    INVALID_PASSWORD = "Invalid password"

    EXPIRED_SIGNATURE = "Expired token"
    INVALID_TOKEN = "Invalid token"
    INVALID_SCOPE = "Invalid scope. Probably, you used access token instead of refresh"

    USER_NOT_FOUND = "User not found"
