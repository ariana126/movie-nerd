class AuthError(Exception):
    pass


class UserAlreadyExists(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class InvalidToken(AuthError):
    pass

