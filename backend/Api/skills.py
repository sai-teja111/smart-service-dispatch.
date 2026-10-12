from fastapi import APIRouter, HTTPException

from Log_config import log
from modules.skills_service import get_all_skills


logger = log()

router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.get("")
def get_skills():
    """Retrieve all available skills."""

    try:
        return get_all_skills()

    except Exception:
        logger.exception("Skills API request failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch skills.",
        )