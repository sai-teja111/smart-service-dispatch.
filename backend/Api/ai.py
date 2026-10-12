
from Log_config import log

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from Api.dependencies import get_current_user
from Api.schemas import AIResponse
from modules.ai_service import answer_ai_question


logger = log()

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
)


class AIQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@router.post(
    "/ask",
    response_model=AIResponse,
)
def ask_ai(
    data: AIQuestion,
    current_user=Depends(get_current_user),
):
    user_uuid = current_user["user_uuid"]
    role = current_user["role"]

    logger.info(
        "AI question received | role: %s",
        role,
    )

    try:
        return answer_ai_question(
            question=data.question,
            user_uuid=user_uuid,
            role=role,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception("AI question processing failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the AI question.",
        )
