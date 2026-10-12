from  sqlmodel import select

from Orm.database import get_session_context
from Orm.skills import Skill as SkillORM

from models.skill_model import Skill


def view_skills():

    try:

        with get_session_context() as session:

            statement = (
                select(SkillORM)
                .order_by(
                    SkillORM.skill_id
                )
            )

            skills = (
                session.exec(statement).all()
            )

            if not skills:

                print(
                    "\nNo Services Available."
                )

                return

            print(
                "\n========== COMPANY SERVICES ==========\n"
            )

            for skill_orm in skills:

                skill_obj = Skill(

                    skill_orm.skill_name,

                    skill_orm.category,

                    skill_orm.difficulty_level,

                    skill_orm.estimated_duration,

                    skill_orm.skill_id
                )

                skill_obj.display_skill()

                print(
                    "-------------------------------------------"
                )

    except Exception as err:

        print(
            "\nError :",
            err
        )