import os.path
from http.client import HTTPException

from fastapi.middleware.cors import CORSMiddleware

from services import FilesHandler

from fastapi import FastAPI, BackgroundTasks, UploadFile, HTTPException, WebSocketException
import services
from models.QuestionData import QuestionData
from services.FilesHandler import process_files_to_vector_db, ask_question
import aiofiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
@app.get("/updateBase", status_code=200)
async def updateVectorBase(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_files_to_vector_db)
    return {"message": "Обработка запущена"}

@app.post("/uploadfile/")
async def upload_file(files: list[UploadFile]):
    files_exist_list = []
    for file in files:
        async with aiofiles.open(f'Docs\\{file.filename}', "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    return {"filename": [file.filename for file in files], "Result": "OK"}


@app.post("/getAnswer/")
async def getAnswer(request: QuestionData):
    return {"question": await ask_question(request.question)}