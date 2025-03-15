from fastapi import FastAPI, BackgroundTasks
import services
from services.pdf_text_parser import get_pdf_text

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/updateBase", status_code=200)
async def update(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_pdf_text, "Docs\\bazi_dannih.pdf")
    #return {"message": await get_pdf_text("Docs\\bazi_dannih.pdf")}
    return {"message": "Обработка запущена"}