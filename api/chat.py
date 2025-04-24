from fastapi import APIRouter, Depends
from core.deps import get_current_active_user
from models.user import User
from schemas.chat import QuestionData, AnswerData

# Импорт функции для работы с вопросами
# Предполагается, что она у вас уже реализована
from services.FilesHandler import ask_question

router = APIRouter()

@router.post("/ask", response_model=AnswerData)
async def get_answer(
    request: QuestionData,
    current_user: User = Depends(get_current_active_user)
):
    """Получение ответа от системы (для всех пользователей)"""
    answer = await ask_question(request.question)
    return {"question": request.question, "answer": answer}