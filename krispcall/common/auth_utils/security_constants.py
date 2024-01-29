import typing

# alphabets without similar looking characters
ALPHABETS: str = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# secret keys
RSA_KEY_SIZE: int = 2048
RSA_PUBLIC_EXPONENT: int = 65537
DSA_KEY_SIZE: int = 2048

# password
PASSWORD_CRYPT_SCHEMES: typing.List[str] = ["bcrypt"]
PASSWORD_STRONG_KIND: str = (
    r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,120})"
)
PASSWORD_MEDIUM_KIND: str = r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,120})"

# jwt : prepend new algorithm if needed
JWT_ALGORITHMS: typing.List[str] = ["RS256"]
JWT_AUTH_TOKEN_LIFETIME_MINUTES = 15
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = 60
JWT_REFRESH_TOKEN_LIFETIME_MINUTES = 600
