import os
import getpass
from glob import glob

from dotenv import load_dotenv, find_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
from langchain.chains import RetrievalQA

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_gigachat.chat_models import GigaChat
from settings import *

db_path = "DATABASE\\"

async def process_files_to_vector_db():
    directory = "Docs\\"
    pdf_files = glob(os.path.join(directory, "*.pdf"))
    documents = []
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            for doc in documents:
                print(f"File: {pdf_file}, Page: {doc.metadata['page']}")
                print("-" * 50)
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=WORDS_FRAGMENTATION_COUNT,
    )
    documents = text_splitter.split_documents(documents)
    model_name = "jinaai/jina-embeddings-v3"
    SentenceTransformer(model_name, trust_remote_code=True)
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'trust_remote_code': True})

    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="RAG",
        client_settings=Settings(anonymized_telemetry=False),
        persist_directory = db_path
    )
    print("Documents db upload done")


async def ask_question(question: str):
    llm = GigaChat(verify_ssl_certs=False)
    load_dotenv(find_dotenv())

    if "GIGACHAT_CREDENTIALS" not in os.environ:
        os.environ["GIGACHAT_CREDENTIALS"] = getpass.getpass("Введите ключ авторизации GigaChat API: ")
    model_name = "jinaai/jina-embeddings-v3"
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'trust_remote_code': True})
    db = Chroma(
        collection_name="RAG",
        embedding_function=embeddings,
        client_settings=Settings(anonymized_telemetry=False),
        persist_directory=db_path
    )
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
    return qa_chain({"query": question})["result"]