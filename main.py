from fastapi import FastAPI
import services
from services.pdf_text_parser import get_pdf_text

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/update")
async def update():
    return {"message": get_pdf_text()}