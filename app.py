from fastapi import FastAPI, Request, Form, UploadFile, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from fastfiles.s3 import S3

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory='templates')
s3 = S3(extra_args={'ACL': 'public-read'})


@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/upload')
async def upload(name: str = Form(), files: S3 = Depends(s3)):
    return RedirectResponse('/', status_code=302)
