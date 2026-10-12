from  getpass import getpass

from  sqlmodel import select

from Orm.database import get_session_context
from Orm.technician import Technician as TechnicianORM
from Orm.technician_skill import TechnicianSkill
from Orm.skills import Skill

from models.technician_model import Technician

from Api.security import hash_password


def register_technician():

    technician_name = input(
        "Enter Technician Name : "
    )

    while True:

        phone = input(
            "Enter Phone Number : "
        )

        if (
            phone.isdigit()
            and len(phone) == 10
            and phone[0] in "6789"
        ):
            break

        print(
            "Invalid Phone Number! "
            "Enter a valid 10-digit mobile number."
        )

    while True:

        password = getpass(
            "Enter Password : "
        )

        if password != password.strip():

            print(
                "Password must not contain "
                "leading or trailing spaces."
            )

            continue

        if len(password) < 8:

            print(
                "Password must contain at least "
                "8 characters."
            )

            continue

        if not any(
            char.isupper()
            for char in password
        ):

            print(
                "Password must contain at least "
                "one uppercase letter."
            )

            continue

        if not any(
            char.islower()
            for char in password
        ):

            print(
                "Password must contain at least "
                "one lowercase letter."
            )

            continue

        if not any(
            char.isdigit()
            for char in password
        ):

            print(
                "Password must contain at least "
                "one digit."
            )

            continue

        if not any(
            not char.isalnum()
            and not char.isspace()
            for char in password
        ):

            print(
                "Password must contain at least "
                "one special character."
            )

            continue

        break

    city = input(
        "Enter City : "
    )

    area = input(
        "Enter Area : "
    )

    pincode = input(
        "Enter Pincode : "
    )

    technician = Technician(
        technician_name,
        phone,
        city,
        area,
        pincode
    )

    try:

        with get_session_context() as session:

            statement = select(
                TechnicianORM
            ).where(
                TechnicianORM.phone == technician.phone
            )

            existing_technician = (
                session.exec(statement).first()
            )

            if existing_technician:

                print(
                    "\nTechnician already exists "
                    "with this phone number."
                )

                return

            password_hash = hash_password(
                password
            )

            technician_orm = TechnicianORM(
                technician_name=technician.name,
                phone=technician.phone,
                password_hash=password_hash,
                city=technician.city,
                area=technician.area,
                pincode=technician.pincode,
                availability="Available",
                workload=0,
                rating=0.0
            )

            session.add(
                technician_orm
            )

            session.flush()

            technician_id = (
                technician_orm.technician_id
            )

            skills_statement = (
                select(Skill)
                .order_by(Skill.skill_id)
            )

            skills = (
                session.exec(
                    skills_statement
                ).all()
            )

            if not skills:

                print(
                    "\nNo Skills Available."
                )

                session.rollback()

                return

            print(
                "\n========== AVAILABLE SKILLS =========="
            )

            for skill in skills:

                print(
                    f"{skill.skill_id}. "
                    f"{skill.skill_name}"
                )

            print(
                "======================================"
            )

            selected_skills = input(
                "\nEnter Skills (comma-separated) : "
            )

            skill_list = (
                selected_skills.split(",")
            )

            for skill_value in skill_list:

                skill_value = (
                    skill_value.strip()
                )

                try:

                    skill_id = int(
                        skill_value
                    )

                except ValueError:

                    print(
                        f"Invalid Skill ID: "
                        f"{skill_value}"
                    )

                    continue

                skill_statement = select(
                    Skill
                ).where(
                    Skill.skill_id == skill_id
                )

                selected_skill = (
                    session.exec(
                        skill_statement
                    ).first()
                )

                if not selected_skill:

                    print(
                        f"Skill ID {skill_id} "
                        "does not exist."
                    )

                    continue

                while True:

                    experience = input(
                        f"Experience for Skill ID "
                        f"{skill_id} (Years): "
                    )

                    if experience.isdigit():

                        experience = int(
                            experience
                        )

                        break

                    print(
                        "Invalid input! "
                        "Please enter only a number."
                    )

                print(
                    "\nExpertise Level"
                )

                print(
                    "1. Beginner"
                )

                print(
                    "2. Intermediate"
                )

                print(
                    "3. Advanced"
                )

                print(
                    "4. Expert"
                )

                while True:

                    choice = input(
                        "Choose : "
                    )

                    if choice == "1":

                        level = "Beginner"

                        break

                    elif choice == "2":

                        level = "Intermediate"

                        break

                    elif choice == "3":

                        level = "Advanced"

                        break

                    elif choice == "4":

                        level = "Expert"

                        break

                    else:

                        print(
                            "Invalid Choice. "
                            "Please select 1-4."
                        )

                technician_skill = TechnicianSkill(
                    technician_id=technician_id,
                    skill_id=skill_id,
                    experience_years=experience,
                    expertise_level=level,
                    is_verified=True
                )

                session.add(
                    technician_skill
                )

            session.commit()

            session.refresh(
                technician_orm
            )

            print(
                "\nTechnician Registered Successfully."
            )

            print(
                f"Technician ID   : "
                f"{technician_orm.technician_id}"
            )

            print(
                f"Technician UUID : "
                f"{technician_orm.technician_uuid}"
            )

    except Exception as err:

        print(
            "\nError :",
            err
        )


def view_technicians():

    try:

        with get_session_context() as session:

            statement = (
                select(TechnicianORM)
                .order_by(
                    TechnicianORM.technician_id
                )
            )

            technicians = (
                session.exec(statement).all()
            )

            if not technicians:

                print(
                    "\nNo Technicians Found."
                )

                return

            print(
                "\n============== TECHNICIAN DETAILS ==============\n"
            )

            for technician_orm in technicians:

                print(
                    f"\nTechnician ID   : "
                    f"{technician_orm.technician_id}"
                )

                print(
                    f"Technician UUID : "
                    f"{technician_orm.technician_uuid}"
                )

                technician = Technician(
                    technician_orm.technician_name,
                    technician_orm.phone,
                    technician_orm.city,
                    technician_orm.area,
                    technician_orm.pincode,
                    technician_orm.availability,
                    technician_orm.workload,
                    technician_orm.rating
                )

                technician.display_technician()

                skill_statement = (
                    select(
                        TechnicianSkill,
                        Skill
                    )
                    .join(
                        Skill,
                        TechnicianSkill.skill_id
                        == Skill.skill_id
                    )
                    .where(
                        TechnicianSkill.technician_id
                        == technician_orm.technician_id
                    )
                    .order_by(
                        Skill.skill_name
                    )
                )

                technician_skills = (
                    session.exec(
                        skill_statement
                    ).all()
                )

                print(
                    "\nSkills:"
                )

                if not technician_skills:

                    print(
                        "No Skills Added."
                    )

                else:

                    for (
                        technician_skill,
                        skill
                    ) in technician_skills:

                        print(
                            f"Skill       : "
                            f"{skill.skill_name}"
                        )

                        print(
                            f"Experience  : "
                            f"{technician_skill.experience_years} Years"
                        )

                        print(
                            f"Expertise   : "
                            f"{technician_skill.expertise_level}"
                        )

                        if technician_skill.is_verified:

                            print(
                                "Verified    : Yes"
                            )

                        else:

                            print(
                                "Verified    : No"
                            )

                        print(
                            "----------------------------------"
                        )

                print(
                    "============================================"
                )

    except Exception as err:

        print(
            "\nError :",
            err
        )


def manage_technician_availability():

    try:

        technician_id = int(
            input(
                "\nEnter Technician ID : "
            )
        )

        with get_session_context() as session:

            technician = session.get(
                TechnicianORM,
                technician_id
            )

            if not technician:

                print(
                    "\nTechnician Not Found."
                )

                return

            technician_name = (
                technician.technician_name
            )

            current_status = (
                technician.availability
            )

            workload = (
                technician.workload or 0
            )

            print(
                "\n========================================"
            )

            print(
                "       TECHNICIAN AVAILABILITY"
            )

            print(
                "========================================"
            )

            print(
                f"Technician ID   : "
                f"{technician_id}"
            )

            print(
                f"Technician Name : "
                f"{technician_name}"
            )

            print(
                f"Current Status  : "
                f"{current_status}"
            )

            print(
                f"Current Workload: "
                f"{workload}"
            )

            print(
                "========================================"
            )

            if workload >= 5:

                print(
                    "\nTechnician has reached "
                    "maximum workload."
                )

                print(
                    "Availability is controlled "
                    "by the system."
                )

                print(
                    "Complete an active service "
                    "to become Available."
                )

                return

            print(
                "\nSelect Availability"
            )

            print(
                "1. Available"
            )

            print(
                "2. Unavailable"
            )

            choice = input(
                "Enter your choice (1-2): "
            )

            if choice == "1":

                new_status = "Available"

            elif choice == "2":

                new_status = "Unavailable"

            else:

                print(
                    "\nInvalid Choice."
                )

                return

            if current_status == new_status:

                print(
                    f"\nTechnician is already "
                    f"{new_status}."
                )

                return

            technician.availability = (
                new_status
            )

            session.commit()

            print(
                "\n========================================"
            )

            print(
                "   AVAILABILITY UPDATED SUCCESSFULLY"
            )

            print(
                "========================================"
            )

            print(
                f"Technician       : "
                f"{technician_name}"
            )

            print(
                f"Previous Status  : "
                f"{current_status}"
            )

            print(
                f"New Status       : "
                f"{new_status}"
            )

            print(
                f"Current Workload : "
                f"{workload}"
            )

            print(
                "========================================"
            )

    except ValueError:

        print(
            "\nInvalid Technician ID."
        )

    except Exception as err:

        print(
            "\nAvailability Error :",
            err
        )
        