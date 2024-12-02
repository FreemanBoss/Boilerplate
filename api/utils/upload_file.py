from asyncio import to_thread
from fastapi import HTTPException, UploadFile
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError

from api.utils.task_logger import create_logger
from api.utils.settings import Config

logger = create_logger("FILE UPLOAD")


# Configure Cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secured=True,
)


async def upload_file_to_cloudinary(
    file: UploadFile,
    folder: str,
    file_name: str,
    file_type: str,
    product_id_prefix: str,
):
    """Uploads a file to Cloudinary and returns the direct download URL.

    Args:
        file (UploadFile): File to upload
        folder (str): Cloudinary folder to store the file in. videos or images

    Returns:
        str: Direct download URL of the uploaded file
    """
    if file_type not in ["video", "image"]:
        raise ValueError("file_type must be either image or video.")
    try:
        product_id_prefix = "videos" if file_type == "video" else "images"
        # Use Cloudinary's uploader to upload the file
        result = await to_thread(
            cloudinary.uploader.upload,
            file=file.file,
            asset_folder=folder,
            resource_type=file_type,
            public_id=file_name,
            product_id_prefix=product_id_prefix,
            use_filename=True,
            use_filename_as_display_name=True,
            unique_filename=False,
            overwrite=False,
        )
        # Get the file URL and append `fl_attachment` for direct download
        return result.get("secure_url")
    except CloudinaryError as exc:
        logger.error("Error uploading file to cloudinary: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"File upload failed") from exc
