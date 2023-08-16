from fastapi import FastAPI, Depends, Form
from fastapi.responses import RedirectResponse
from filestore import Store
from dotenv import load_dotenv

from .utils import book, author, cover, lib

load_dotenv()
app = FastAPI()


@app.get("/")
async def home():
    return RedirectResponse(url="/docs")


@app.post("/uploadbook")
async def upload_book(model=Depends(book.model), bk=(Depends(book))) -> Store:
    return bk.store


@app.post("/uploadauthor")
async def upload_author(model=Depends(author.model), res=Depends(author)) -> Store:
    return res.store


@app.post("/uploadcover")
async def upload_cover(model=Depends(cover.model), res=Depends(cover)) -> Store:
    return res.store


@app.post("/uploadlib")
async def upload_lib(book_name: str = Form(), model=Depends(lib.model), res=Depends(lib)) -> Store:
    return res.store
