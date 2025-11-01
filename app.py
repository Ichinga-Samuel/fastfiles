from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from fastfiles import S3, Local, Memory, FileData

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory='.')

s3 = S3(config={'extra-args': {'ACL': 'public-read'}})
local = Local(config={"dest": "test/uploads/check"})
memory = Memory()


@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/s3_upload', name='s3_upload')
async def upload(file: FileData = Depends(s3)) -> FileData:
    return file


@app.post('/local_upload', name='local_upload')
async def upload(files: list[FileData] = Depends(local)) -> list[FileData]:
    return files


@app.post('/memory_upload', name='memory_upload')
async def upload(file: FileData = Depends(memory)) -> FileData:
    return file
