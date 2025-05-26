import getpass
import os

from chromadb import Settings, logger
from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter, Depends
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_chroma import Chroma
from langchain_gigachat import GigaChat
from langchain_openai import OpenAIEmbeddings

from core.deps import get_current_active_user
from models.user import User
from schemas.chat import QuestionData, AnswerData
from config import settings

router = APIRouter()

@router.post("/ask", response_model=AnswerData)
async def get_answer(
    request: QuestionData,
    current_user: User = Depends(get_current_active_user)
):
    # Set DB path based on configuration (None when using MongoDB)
    db_path = None if settings.USE_MONGODB else "DATABASE\\"
    
    llm = GigaChat(verify_ssl_certs=False)
    load_dotenv(find_dotenv())

    if "GIGACHAT_CREDENTIALS" not in os.environ:
        os.environ["GIGACHAT_CREDENTIALS"] = getpass.getpass("Введите ключ авторизации GigaChat API: ")

    try:
        embeddings = OpenAIEmbeddings()

        if settings.USE_MONGODB:
            # Use MongoDB for vector search
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(
                    anonymized_telemetry=False
                ),
            )
        else:
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(
                    anonymized_telemetry=False,
                ),
                persist_directory=db_path
            )
            logger.info("Using local Chroma")

        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 20}
        )

        from langchain.prompts import PromptTemplate
        prompt_template = """ Не используй markdown. Используй только следующий контекст для ответа на вопрос. Если ты не можешь найти ответ в контексте, прямо скажи "Я не могу найти ответ в предоставленных документах".
        В ответе не должно быть ничего лишнего, только ответ на вопрос без дополнительных указаний.

    Контекст:
    {context}

    Вопрос: {question}
    Ответ: """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        answer = qa_chain({"query": request.question})

        print(f"Использованные документы: {answer['source_documents']}")

    except Exception as e:
        print(f"Ошибка при инициализации OpenAI: {e}")

        from langchain_huggingface import HuggingFaceEmbeddings

        model_name = "jinaai/jina-embeddings-v3"
        embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'trust_remote_code': True})

        if settings.USE_MONGODB:
            # Use MongoDB for vector search
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(
                    anonymized_telemetry=False
                ),
            )
        else:
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(
                    anonymized_telemetry=False,
                ),
                persist_directory=db_path
            )
            logger.info("Using local Chroma")

        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 20}
        )

        from langchain.prompts import PromptTemplate
        prompt_template = """ Не используй markdown. Используй только следующий контекст для ответа на вопрос. Если ты не можешь найти ответ в контексте, прямо скажи "Я не могу найти ответ в предоставленных документах".
        В ответе не должно быть ничего лишнего, только ответ на вопрос без дополнительных указаний.

    Контекст:
    {context}

    Вопрос: {question}
    Ответ: """
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        answer = qa_chain({"query": request.question})

        print(f"Использованные документы: {answer['source_documents']}")

    return {"question": request.question, "answer": answer["result"]}