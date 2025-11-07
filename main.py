from pathlib import Path
import uuid
import uvicorn
from fastapi import FastAPI, Depends, Request, UploadFile
from fastapi.datastructures import FormData
from fastapi.openapi.models import OpenAPI
from filestore import LocalStorage, Store, FileStore, FileField, MemoryStorage, Config, LocalEngine, MemoryEngine
from filestore.util import FileModel
from filestore.s3 import S3Storage, S3Engine
from dotenv import load_dotenv
import os
load_dotenv()
app = FastAPI()
print(os.getenv("AWS_BUCKET_NAME"))
# 1. Define the storage dependency.
# This will accept a form field named "file".
# It will allow a max of 1 file (count=1).
# Files will be saved in the "./uploads" directory.
storage = LocalStorage(
    name="file",
    count=1,
    required=True,
    config={"destination": "uploads/"}
)


@app.post("/upload/")
async def upload_single_file(file_store: Store = Depends(storage)):
    """
    Upload a single file to local storage.

    The 'file_store' dependency handles everything:
    - Parses the multipart/form-data
    - Finds the "file" field
    - Saves it to "uploads/" using LocalEngine
    - Returns a 'Store' object
    """
    if file_store.status:
        return {
            "message": "File uploaded successfully",
            "data": file_store.files
        }
    else:
        return {
            "message": "Upload failed",
            "error": file_store.error
        }


# Accepts up to 10 files from the "gallery_images" field
gallery_storage = LocalStorage(
    name="gallery_images",
    count=10,
    config={"destination": "uploads/gallery"}
)

@app.post("/upload-gallery/")
async def upload_gallery(file_store: Store = Depends(gallery_storage)):
    # file_store.files["gallery_images"] will be a list of FileData objects
    return file_store

# Define configuration for multiple, different fields
multi_field_storage = FileStore(fields=[
    FileField(
        name="avatar",
        max_count=1,
        required=True,
        config={"destination": "uploads/avatars"}
    ),
    FileField(
        name="resume",
        max_count=1,
        required=False,
        config={"destination": "uploads/resumes"}
    )
])

@app.post("/upload-profile/")
async def upload_profile(file_store: Store = Depends(multi_field_storage)):
    # Results are keyed by field name
    # file_store.files["avatar"] -> list[FileData]
    # file_store.files["resume"] -> list[FileData] (or not present if not required/uploaded)
    return file_store


mem_storage = MemoryStorage(name="profile_pic", count=1)


@app.post("/upload-memory/")
async def upload_to_memory(file_store: Store = Depends(mem_storage)):
    if file_store.status:
        # Get the first (and only) file from the "profile_pic" field
        file_data = file_store.files["profile_pic"][0]

        # Access the file bytes directly from the .file attribute
        file_bytes: bytes = file_data.file

        # You could now process these bytes, e.g.:
        # from PIL import Image
        # import io
        # image = Image.open(io.BytesIO(file_bytes))

        return {
            "message": "File processed in memory",
            "filename": file_data.filename,
            "size": file_data.size
        }
    return file_store

# Define the S3 config.
# Config is a TypedDict from filestore.datastructures
s3_config = dict(
    destination="user-uploads/",  # Path/prefix within the bucket
    # You can add 'extra_args' for S3, e.g., for public files
    # extra_args={"ACL": "public-read"}
)

s3_storage = S3Storage(name="document", config=s3_config, count=1)

@app.post("/upload-s3/")
async def upload_to_s3(file_store: Store = Depends(s3_storage)):
    # The 'url' attribute will be populated with the S3 file URL
    return file_store


def get_user_upload_path(
    request: Request,
    form: FormData,
    field_name: str,
    file: UploadFile
) -> Path:
    """Saves file to a user-specific folder, e.g., 'uploads/user_123/'"""
    # This is a simple example. In a real app, you'd get
    # the user ID from a token in the request.
    user_id = request.headers.get("X-User-ID", "anonymous")
    user_dir = Path(f"uploads/users/{user_id}")
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / file.filename

# Pass the function as the destination
dynamic_storage = LocalStorage(
    name="user_file",
    config=dict(destination=get_user_upload_path)
)

@app.post("/upload-dynamic-path/")
async def upload_dynamic_path(file_store: Store = Depends(dynamic_storage)):
    return file_store

def unique_filename(
    request: Request,
    form: FormData,
    field_name: str,
    file: UploadFile
) -> UploadFile:
    """Renames the file to a unique UUID, keeping its extension."""
    ext = Path(file.filename).suffix
    file.filename = f"{uuid.uuid4()}{ext}"
    return file  # Return the modified file object

rename_storage = LocalStorage(
    name="data",
    config=dict(
        destination="uploads/data",
        filename=unique_filename # Add the filename callable
    )
)

@app.post("/upload-renamed/")
async def upload_renamed(file_store: Store = Depends(rename_storage)):
    # The 'filename' in the FileData response will be the new UUID
    return file_store

def check_is_image(
    request: Request,
    form: FormData,
    field_name: str,
    file: UploadFile
) -> bool:
    """Only allow JPEG or PNG files."""
    return file.content_type in ["image/jpeg", "image/png"]

# A second filter, just to show a list
def check_not_empty(
    request: Request,
    form: FormData,
    field_name: str,
    file: UploadFile
) -> bool:
    """Rejects zero-byte files."""
    return file.size > 0

image_storage = LocalStorage(
    name="image",
    count=4,
    config=Config(
        destination="uploads/images_only",
        filters=[check_is_image, check_not_empty] # Add the filter list
    )
)

@app.post("/upload-image-only/")
async def upload_image_only(file_store: Store = Depends(image_storage)):
    # Files that fail the filter will not be in the response
    return file_store


multi_engine_storage = FileStore(fields=[
    FileField(
        name="avatar",
        max_count=1,
        required=True,
        config=Config(
            StorageEngine=LocalEngine,  # <-- Use LocalEngine
            destination="uploads/avatars"
        )
    ),
    FileField(
        name="resume",
        max_count=1,
        required=False,
        config=Config(
            StorageEngine=S3Engine,  # <-- Use S3Engine
            destination="resumes/",  # <-- Path/prefix in bucket
        )
    ),
    FileField(
        name="config_file",
        max_count=1,
        required=False,
        config=Config(
            StorageEngine=MemoryEngine  # <-- Use MemoryEngine
            # No destination needed
        )
    )
])


@app.post("/upload-all-at-once/")
async def upload_multi_engine(file_store: Store = Depends(multi_engine_storage),
                              open_api_form = Depends(FileModel(multi_engine_storage))):
    """
    Upload files to three different storage backends in one request.

    - 'avatar' -> Local Disk ('uploads/avatars/')
    - 'resume' -> Amazon S3 ('my-awesome-bucket/resumes/')
    - 'config_file' -> In-Memory (bytes)
    """

    # The 'file_store.files' dict will have keys for each field
    # that was successfully processed.

    response_data = {}

    if "avatar" in file_store.files:
        # This FileData object will have its 'path' attribute set
        response_data["avatar_path"] = file_store.files["avatar"][0].path

    if "resume" in file_store.files:
        # This FileData object will have its 'url' attribute set
        response_data["resume_url"] = file_store.files["resume"][0].url

    if "config_file" in file_store.files:
        # This FileData object will have its 'file' attribute (bytes) set
        response_data["config_file_size"] = file_store.files["config_file"][0].size
        # You could now read the bytes:
        # config_bytes = file_store.files["config_file"][0].file

    return {
        "status": file_store.status,
        "uploads": response_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

