from  sqlmodel import select

from Orm.database import get_session_context
from Orm.skills import Skill

from modules.chroma_service import add_service_to_chroma


def load_services_to_chroma():

    try:

        with get_session_context() as session:

            statement = (
                select(Skill)
                .order_by(Skill.skill_id)
            )

            skills = session.exec(statement).all()

            if not skills:

                print(
                    "\nNo services found in skills table."
                )

                return

            for skill in skills:

                add_service_to_chroma(
                    skill.skill_id,
                    skill.skill_name,
                    skill.category,
                    skill.description or ""
                )

            print(
                f"\n{len(skills)} services loaded into Chroma successfully."
            )

    except Exception as err:

        print(
            "\nChroma Setup Error :",
            err
        )