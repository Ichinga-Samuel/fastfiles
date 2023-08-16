from fastapi import UploadFile, Request
from starlette.datastructures import FormData
from filestore import LocalStorage, S3Storage, MemoryStorage


def book_filename(req: Request, form: FormData, field: str, file: UploadFile) -> UploadFile:
    book_name = form.get('book_name')
    fn = file.filename
    start = fn.rfind('.')
    file.filename = f'{book_name}{fn[start:]}'
    return file


def book_filter(req: Request, form: FormData, field: str, file: UploadFile) -> bool:
    fn = file.filename
    return fn.endswith('.pdf') or fn.endswith('.epub')


def book_destination(req: Request, form: FormData, field: str, file: UploadFile) -> str:
    bn = form.get('book_name')
    return f'Books/{bn.title()}/{file.filename}'


def image_filter(req: Request, form: FormData, field: str, file: UploadFile) -> bool:
    fn = file.filename
    return (fn.endswith('.jpg') or fn.endswith('.png') or fn.endswith('.jpeg')) and file.size <= 2097152  # 2MB


def cover_destination(req: Request, form: FormData, field: str, file: UploadFile) -> str:
    fn = file.filename
    bn = form.get('book_name')
    return f'Books/{bn.title()}/Covers/{fn}'


def author_destination(req: Request, form: FormData, field: str, file: UploadFile) -> str:
    fn = file.filename
    bn = form.get('book_name')
    return f'Books/{bn.title()}/Authors/{fn}'


book = S3Storage(name='book', required=True, config={'filter': book_filter, 'destination': book_destination,
                                                     'filename': book_filename})

author = LocalStorage(name='author', count=3, config={'filter': image_filter, 'dest': 'uploads/Authors/'})

cover = MemoryStorage(fields=[{'name': 'front_cover', 'required': True, 'max_count': 2},
                              {'name': 'back_cover', 'max_count': 1}],
                      config={'filter': lambda req, form, field, file: file.size <= 524288})


fields = [{'name': 'front_cover', 'required': True, 'max_count': 2}, {'name': 'back_cover', 'max_count': 1},
          {'name': 'book', 'required': True, 'max_count': 1, 'config': {'filter': book_filter,
                                                                        'destination': book_destination,
                                                                        'filename': book_filename,
                                                                        'background': True}},
          {'name': 'author', 'required': True, 'max_count': 3, 'config': {'destination': author_destination}}]

lib = S3Storage(fields=fields, config={'filter': image_filter, 'destination': cover_destination})
