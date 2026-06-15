import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# Importar SDK de Cloudinary
import cloudinary
import cloudinary.uploader
from src.database.profile import update_profile_picture, get_profile_picture_url

# Configure Cloudinary.
# Credentials will be picked up automatically from environment variables:
# CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    cloudinary.config( 
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
        api_key = os.getenv("CLOUDINARY_API_KEY"), 
        api_secret = os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

def extract_public_id(url: str) -> str:
    if not url or "res.cloudinary.com" not in url:
        return None
    try:
        parts = url.split("/image/upload/")
        if len(parts) < 2:
            return None
        path = parts[1]
        path_without_ext = path.rsplit(".", 1)[0]
        path_segments = path_without_ext.split("/")
        if path_segments[0].startswith("v") and path_segments[0][1:].isdigit():
            public_id = "/".join(path_segments[1:])
        else:
            public_id = "/".join(path_segments)
        return public_id
    except Exception as e:
        print("Error extracting public id:", e)
        return None

router = APIRouter(prefix="/profile")

@router.post("/upload_picture/")
async def upload_picture(id_employees: int = Form(...), file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo no es una imagen")
            
        # Get old image URL from database
        old_url = get_profile_picture_url(id_employees)
            
        # Upload image to Cloudinary
        result = cloudinary.uploader.upload(file.file, folder="clinica_remes_profiles")
        url = result.get("secure_url")
        
        if not url:
            raise HTTPException(status_code=500, detail="Error al obtener la URL de la imagen")
            
        # Update database
        success = update_profile_picture(id_employees, url)
        if not success:
            raise HTTPException(status_code=500, detail="Error al actualizar la base de datos")
            
        # If database update was successful, delete old picture from Cloudinary
        if old_url:
            public_id = extract_public_id(old_url)
            if public_id:
                try:
                    cloudinary.uploader.destroy(public_id)
                    print(f"Deleted old profile picture from Cloudinary: {public_id}")
                except Exception as del_err:
                    print("Error deleting old profile picture from Cloudinary:", del_err)
            
        return {"ok": True, "url": url}
    except HTTPException as he:
        print("Error en upload_picture (HTTPException):", he.detail)
        return {"ok": False, "error": he.detail}
    except Exception as e:
        print("Error en upload_picture:", e)
        return {"ok": False, "error": str(e)}

@router.post("/delete_picture/")
async def delete_picture(id_employees: int = Form(...)):
    try:
        # Get old image URL from database
        old_url = get_profile_picture_url(id_employees)
        
        # Update database to set profile_picture to NULL
        success = update_profile_picture(id_employees, None)
        if not success:
            raise HTTPException(status_code=500, detail="Error al actualizar la base de datos")
            
        # Delete old image from Cloudinary
        if old_url:
            public_id = extract_public_id(old_url)
            if public_id:
                try:
                    cloudinary.uploader.destroy(public_id)
                    print(f"Deleted profile picture from Cloudinary: {public_id}")
                except Exception as del_err:
                    print("Error deleting profile picture from Cloudinary:", del_err)
                    
        return {"ok": True, "url": None}
    except HTTPException as he:
        print("Error en delete_picture (HTTPException):", he.detail)
        return {"ok": False, "error": he.detail}
    except Exception as e:
        print("Error en delete_picture:", e)
        return {"ok": False, "error": str(e)}

