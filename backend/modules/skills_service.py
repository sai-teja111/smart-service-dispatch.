from sqlmodel import select

from Log_config import log
from Orm.database import get_session_context
from Orm.skills import Skill


logger = log()


def get_all_skills() -> list[dict]:
    """Fetch all skills from the database."""

    logger.info("Fetching all skills")

    try:
        with get_session_context() as session:
            statement = select(Skill).order_by(Skill.skill_id)
            skills = session.exec(statement).all()

            result = [
                {
                    "skill_id": skill.skill_id,
                    "skill_name": skill.skill_name,
                    "category": skill.category,
                    "difficulty_level": skill.difficulty_level,
                    "estimated_duration": skill.estimated_duration,
                    "description": skill.description,
                }
                for skill in skills
            ]

            logger.info(
                "Skills fetched successfully | count: %s",
                len(result),
            )

            return result

    except Exception:
        logger.exception("Failed to fetch skills")
        raise