
from datetime import datetime, timezone

from sqlmodel import select

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.technician import Technician
from Orm.technician_skill import TechnicianSkill
from Orm.skills import Skill

from Api.security import hash_password, verify_password

from modules.notifications_service import notify_active_admins


# ============================================================
# CUSTOMER REGISTRATION
# ============================================================

def register_customer_user(data):
    with get_session_context() as session:
        existing_customer = session.exec(
            select(Customer).where(
                Customer.phone == data.phone
            )
        ).first()

        if existing_customer:
            raise ValueError(
                "Customer with this phone number already exists."
            )

        customer = Customer(
            customer_name=data.customer_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            city=data.city,
            area=data.area,
            pincode=data.pincode,
        )

        session.add(customer)
        session.commit()
        session.refresh(customer)

        return customer


# ============================================================
# TECHNICIAN REGISTRATION
# ============================================================

def register_technician_user(data):
    """
    Register a technician with Pending approval status.

    Submitted skills remain unverified until Admin reviews them.
    Notify active administrators after registration commits.
    """

    with get_session_context() as session:
        existing_technician = session.exec(
            select(Technician).where(
                Technician.phone == data.phone
            )
        ).first()

        if existing_technician:
            raise ValueError(
                "Technician with this phone number already exists."
            )

        technician = Technician(
            technician_name=data.technician_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            city=data.city,
            area=data.area,
            pincode=data.pincode,
            approval_status="Pending",
        )

        session.add(technician)

        # Generate technician_id before inserting skill records.
        session.flush()

        for skill_data in data.skills:
            skill = session.exec(
                select(Skill).where(
                    Skill.skill_id == skill_data.skill_id
                )
            ).first()

            if not skill:
                raise ValueError(
                    f"Skill with ID {skill_data.skill_id} "
                    f"does not exist."
                )

            technician_skill = TechnicianSkill(
                technician_id=technician.technician_id,
                skill_id=skill.skill_id,
                experience_years=skill_data.experience_years,
                expertise_level=skill_data.expertise_level,
                is_verified=False,
            )

            session.add(technician_skill)

        # Save the technician and skill associations together.
        session.commit()
        session.refresh(technician)

        # Capture the name while the registration session is open.
        technician_name = technician.technician_name

    # Notify admins only after the registration transaction commits.
    # A notification failure must not undo a successful registration.
    try:
        notify_active_admins(
            title="New Technician Registration",
            message=(
                f"{technician_name} registered and is awaiting "
                "admin approval and skill verification."
            ),
            notification_type="TECHNICIAN_REGISTRATION",
        )
    except Exception:
        # The notification service logs the failure.
        # Keep registration successful if notification delivery fails.
        pass

    return technician


# ============================================================
# CUSTOMER AUTHENTICATION
# ============================================================

def authenticate_customer(phone, password):
    with get_session_context() as session:
        customer = session.exec(
            select(Customer).where(
                Customer.phone == phone
            )
        ).first()

        if not customer:
            return None

        if not verify_password(
            password,
            customer.password_hash,
        ):
            return None

        # Determine whether this is the first tracked login.
        first_login = customer.last_login_at is None

        # Record the current successful login time in UTC.
        customer.last_login_at = datetime.now(timezone.utc)

        session.add(customer)
        session.commit()
        session.refresh(customer)

        return customer, first_login


# ============================================================
# TECHNICIAN AUTHENTICATION
# ============================================================

def authenticate_technician(phone, password):
    with get_session_context() as session:
        technician = session.exec(
            select(Technician).where(
                Technician.phone == phone
            )
        ).first()

        if not technician:
            return None

        if not verify_password(
            password,
            technician.password_hash,
        ):
            return None

        # Return the account status separately so the API can
        # show the correct message without issuing a token.
        if technician.approval_status == "Pending":
            return {
                "status": "pending",
            }

        if technician.approval_status == "Rejected":
            return {
                "status": "rejected",
            }

        if technician.approval_status != "Approved":
            return {
                "status": "pending",
            }

        # Determine whether this is the first tracked login.
        first_login = technician.last_login_at is None

        # Record the current successful login time in UTC.
        technician.last_login_at = datetime.now(timezone.utc)

        session.add(technician)
        session.commit()
        session.refresh(technician)

        return technician, first_login