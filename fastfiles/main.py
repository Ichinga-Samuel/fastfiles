from abc import ABC, abstractmethod

from fastapi import UploadFile, Depends
from pydantic import BaseModel, HttpUrl


class FileData(BaseModel):
    public_url: HttpUrl | str = ""
    status: bool = True


class CloudUpload(ABC):
    def __init__(self, file: bytes | UploadFile or None = None, files: list[UploadFile | bytes] or None = None, extra_args: dict or None = None,
                 name: str = ""):
        self.file = file
        self.files = files
        self.response: FileData | list[FileData] = FileData()
        self.extra_args = extra_args or {}
        self.name = name

    async def __call__(self,  file: UploadFile or None = None, files: list[UploadFile] or None = None, name: str = ""):
        if file:
            self.file = file
            await self.upload(name=name)
        elif files:
            self.files = files
            await self.multi_upload()
        return self

    @abstractmethod
    async def upload(self, name: str = ""):
        """"""

    @abstractmethod
    async def multi_upload(self, *args, **kwargs):
        """"""
