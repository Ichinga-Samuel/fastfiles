from abc import ABC, abstractmethod

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl


class FileData(BaseModel):
    """
    Represents the result of an upload operation
    Attributes:
        public_url (HttpUrl | str): A public URL for accessing the object
        status (bool): True if the upload is successful else False.
    """
    public_url: HttpUrl | str = ""
    status: bool = False


class CloudUpload(ABC):
    """
    Methods:
        upload: Uploads a single object to the cloud
        multi_upload: Upload multiple objects to the cloud

    Attributes:
        result (FileData | list[FileData]): Result of the file upload operation.
        A single FileData object for a single upload and a list of FileData objects for multiple uploads.
    """

    def __init__(self, config: dict | None = None):
        """"
        Keyword Args:
            config (dict): A dictionary of config settings
        """"
        self.result: FileData | list[FileData] = FileData()
        self.config = config or {}
        
    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileData | list[FileData]:
        try:
            if file:
                await self.upload(file)
    
            elif files:
                await self.multi_upload(files=files)
        except Exception as err:
            pass
        return self.result

    @abstractmethod
    async def upload(self, *, file: UploadFile | None = None) -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """"""
