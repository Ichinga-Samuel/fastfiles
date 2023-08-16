"""
Memory storage for FastStore. This storage is used to store files in memory.
"""
import asyncio
from logging import getLogger

from .main import CloudUpload, FileData
from fastapi import UploadFile

logger = getLogger()


class Memory(CloudUpload):
    """
    Memory storage for FastAPI.
    This storage is used to store files in memory and returned as bytes.
    """
    async def upload(self, *, file: UploadFile) -> FileData:
        try:
            file_object = await file.read()
            return FileData(size=file.size, filename=file.filename, content_type=file.content_type, file=file_object,
                            message=f'{file.filename} saved successfully')
        except Exception as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            return FileData(status=False, error=str(err), message='Unable to save file')

    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        return list(await asyncio.gather(*[self.upload(file=file) for file in files]))
