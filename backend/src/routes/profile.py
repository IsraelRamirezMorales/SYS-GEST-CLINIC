import logging
import os
from typing import Optional

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from src.database.profile import get_profile_picture_url, update_profile_picture
from src.utils.security import CurrentUser, get_current_user

logger = logging.getLogger(__name__)

# Credenciales desde variables de entorno:
# CLOUDINARY_URL o CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

PROFILE_FOLDER = "sys_gest_clinic_profiles"
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/profile")


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"ok": False, "error": message})


def _is_image(data: bytes) -> bool:
    """Valida por firma del archivo (el content-type lo controla el cliente)."""
    return (
        data.startswith(b"\xff\xd8\xff")  # JPEG
        or data.startswith(b"\x89PNG\r\n\x1a\n")  # PNG
        or data[:6] in (b"GIF87a", b"GIF89a")  # GIF
        or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")  # WEBP
    )


def extract_public_id(url: Optional[str]) -> Optional[str]:
    """Solo devuelve public_ids dentro de la carpeta de perfiles de esta app."""
    if not url or "res.cloudinary.com" not in url:
        return None
    parts = url.split("/image/upload/")
    if len(parts) < 2:
        return None
    segments = parts[1].rsplit(".", 1)[0].split("/")
    if segments and segments[0].startswith("v") and segments[0][1:].isdigit():
        segments = segments[1:]
    public_id = "/".join(segments)
    return public_id if public_id.startswith(PROFILE_FOLDER + "/") else None


def _destroy_old(url: Optional[str]) -> None:
    public_id = extract_public_id(url)
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        logger.exception("No se pudo borrar la foto anterior de Cloudinary")


@router.post("/upload_picture/")
def upload_picture(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user)):
    data = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        return _error(413, "La imagen supera el tamaño máximo de 5 MB")
    if not _is_image(data):
        return _error(400, "El archivo no es una imagen válida")

    try:
        old_url = get_profile_picture_url(user.id_employees)
        result = cloudinary.uploader.upload(data, folder=PROFILE_FOLDER, resource_type="image")
        url = result.get("secure_url")
        if not url:
            return _error(502, "No se pudo subir la imagen")
        update_profile_picture(user.id_employees, url)
    except Exception:
        logger.exception("Error en upload_picture")
        return _error(500, "No se pudo actualizar la foto de perfil")

    _destroy_old(old_url)
    return {"ok": True, "url": url}


@router.post("/delete_picture/")
def delete_picture(user: CurrentUser = Depends(get_current_user)):
    try:
        old_url = get_profile_picture_url(user.id_employees)
        update_profile_picture(user.id_employees, None)
    except Exception:
        logger.exception("Error en delete_picture")
        return _error(500, "No se pudo eliminar la foto de perfil")

    _destroy_old(old_url)
    return {"ok": True, "url": None}
