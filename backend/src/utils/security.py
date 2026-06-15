from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    Supports fallback to plain text comparison for legacy passwords.
    """
    if not hashed_password:
        return False
    try:
        if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        pass
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """
    Generates a bcrypt hash of the password.
    """
    return pwd_context.hash(password)
