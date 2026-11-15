"""
Autenticación y utilidades de seguridad.

- Hash de contraseñas con bcrypt (sin passlib: passlib 1.7.4 es incompatible con bcrypt>=4.1
  y hacía que el hash fallara en silencio, dejando las contraseñas en texto plano).
- Emisión/validación de JWT. El token es la única fuente de verdad sobre quién hace la
  petición: el backend nunca debe confiar en un id_employees enviado por el cliente.
- Limitador de intentos de login en memoria.
"""
import hmac
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# ── Contraseñas ────────────────────────────────────────────────────────────

_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")
# Hash ficticio para igualar el tiempo de respuesta cuando el usuario no existe.
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt()).decode()


def is_hashed(stored: Optional[str]) -> bool:
    return bool(stored) and stored.startswith(_BCRYPT_PREFIXES)


def verify_password(plain_password: str, stored_password: Optional[str]) -> bool:
    """
    Verifica una contraseña. Si el valor guardado es un hash bcrypt se valida SOLO con
    bcrypt (nunca se compara el texto contra el hash). Las contraseñas legacy en texto
    plano se comparan en tiempo constante para poder migrarlas a hash en el login.
    """
    if not stored_password:
        bcrypt.checkpw(b"x", _DUMMY_HASH.encode())
        return False
    if is_hashed(stored_password):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_password.encode("utf-8"))
        except ValueError:
            # Contraseña > 72 bytes o hash corrupto.
            return False
    return hmac.compare_digest(plain_password.encode("utf-8"), stored_password.encode("utf-8"))


def burn_password_check() -> None:
    """Gasta el mismo tiempo que una verificación real (usuario inexistente)."""
    bcrypt.checkpw(b"x", _DUMMY_HASH.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── JWT ────────────────────────────────────────────────────────────────────

_JWT_ALGORITHM = "HS256"
_JWT_TTL_HOURS = int(os.getenv("JWT_TTL_HOURS", "8"))
_JWT_SECRET = os.getenv("JWT_SECRET")
if not _JWT_SECRET:
    _JWT_SECRET = secrets.token_urlsafe(64)
    logger.warning(
        "JWT_SECRET no está definido: se generó uno temporal. Las sesiones se invalidarán "
        "al reiniciar el servidor. Define JWT_SECRET en producción."
    )


@dataclass(frozen=True)
class CurrentUser:
    id_employees: int
    role: Optional[str]
    fisio_type: Optional[str]
    # Doctor cuyos pacientes puede ver este usuario (él mismo si es doctor,
    # su doctor asignado si es fisio).
    scope_doctor: int

    @property
    def is_acuatic(self) -> bool:
        # Los fisios de alberca atienden a pacientes de todas las doctoras.
        return self.fisio_type == "Acuática"


def create_access_token(user: CurrentUser) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id_employees),
        "role": user.role,
        "fisio": user.fisio_type,
        "doc": user.scope_doctor,
        "iat": now,
        "exp": now + timedelta(hours=_JWT_TTL_HOURS),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _UNAUTHORIZED
    try:
        payload = jwt.decode(
            credentials.credentials,
            _JWT_SECRET,
            algorithms=[_JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        return CurrentUser(
            id_employees=int(payload["sub"]),
            role=payload.get("role"),
            fisio_type=payload.get("fisio"),
            scope_doctor=int(payload["doc"]),
        )
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise _UNAUTHORIZED


# ── Limitador de intentos de login ─────────────────────────────────────────

class LoginRateLimiter:
    """
    Bloquea temporalmente un usuario o una IP tras demasiados intentos fallidos.
    En memoria: suficiente para una sola instancia. Con varias instancias, mover a Redis.
    """

    def __init__(self, max_per_user: int = 5, max_per_ip: int = 20, window_seconds: int = 900):
        self.max_per_user = max_per_user
        self.max_per_ip = max_per_ip
        self.window = window_seconds
        self._failures: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> list[float]:
        attempts = [t for t in self._failures.get(key, []) if now - t < self.window]
        if attempts:
            self._failures[key] = attempts
        else:
            self._failures.pop(key, None)
        return attempts

    def is_blocked(self, username: str, ip: str) -> bool:
        now = time.monotonic()
        with self._lock:
            return (
                len(self._recent(f"u:{username.lower()}", now)) >= self.max_per_user
                or len(self._recent(f"ip:{ip}", now)) >= self.max_per_ip
            )

    def register_failure(self, username: str, ip: str) -> None:
        now = time.monotonic()
        with self._lock:
            for key in (f"u:{username.lower()}", f"ip:{ip}"):
                self._failures.setdefault(key, []).append(now)

    def reset(self, username: str) -> None:
        with self._lock:
            self._failures.pop(f"u:{username.lower()}", None)


login_rate_limiter = LoginRateLimiter()
