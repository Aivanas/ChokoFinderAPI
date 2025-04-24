from pydantic import BaseModel

class QuestionData(BaseModel):
    question: str

class AnswerData(BaseModel):
    question: str
    answer: str