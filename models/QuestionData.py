import pydantic
from pydantic import BaseModel


class QuestionData(BaseModel):
    question: str