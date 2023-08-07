import asyncio
from logging import getLogger

from .main import CloudUpload, FileData, Path
from fastapi import UploadFile

logger = getLogger()


class Local(CloudUpload):
    """
    Local storage for FastAPI.
    """
    async def upload(self, *, file: UploadFile) -> FileData:
        """
        Upload a file to the destination.

        Args:
            file UploadFile: File to upload

        Returns:
            FileData: Result of file upload
        """
        try:
            dest = self.config.get('dest') or Path('uploads') / f'{file.filename}'
            file_object = await file.read()
            with open(f'{dest}', 'wb') as fh:
                fh.write(file_object)
            await file.close()
            return FileData(path=dest, message=f'{file.filename} saved successfully', content_type=file.content_type,
                            size=file.size, filename=file.filename)
        except Exception as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            return FileData(status=False, error=str(err), message=f'Unable to save file')

    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileData]:
        """
        Upload multiple files to the destination.

        Args:
            files (list[tuple[str, UploadFile]]): A list of tuples of field name and the file to upload.

        Returns:
            list[FileData]: A list of uploaded file data
        """
        res = await asyncio.gather(*[self.upload(file=file) for file in files])
        return list(res)
