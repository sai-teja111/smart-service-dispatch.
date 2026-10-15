from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select

from Api.admin_schemas import AdminLogin, AdminProvision
from Api.jwt import create_access_token
from Api.security import hash_password, verify_password

from Orm.admin import Admin
from Orm.customer import Customer
from Orm.service_request import ServiceRequest
from Orm.technician import Technician
from Orm.technician_skill import TechnicianSkill
from Orm.skills import Skill
from Orm.database import get_session_context


# ============================================================
# ADMIN PROVISIONING
# ============================================================

def provision_initial_admin(
    admin_data: AdminProvision,
) -> dict:
    """Create the initial administrator account."""

    with get_session_context() as session:
        existing_admin = session.exec(
            select(Admin)
        ).first()

        if existing_admin is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An admin account has already been provisioned.",
            )

        email = str(admin_data.email).strip().lower()
        password_hash = hash_password(admin_data.password)

        admin = Admin(
            admin_name=admin_data.admin_name,
            email=email,
            password_hash=password_hash,
            is_active=True,
        )

        session.add(admin)
        session.commit()
        session.refresh(admin)

        return {
            "admin_uuid": str(admin.admin_uuid),
            "admin_name": admin.admin_name,
            "email": admin.email,
            "is_active": admin.is_active,
        }


# ============================================================
# ADMIN LOGIN
# ============================================================

def login_admin(
    login_data: AdminLogin,
) -> dict:
    """Authenticate an administrator and issue an access token."""

    email = str(login_data.email).strip().lower()

    with get_session_context() as session:
        statement = select(Admin).where(
            Admin.email == email
        )

        admin = session.exec(statement).first()

        if admin is None or not verify_password(
            login_data.password,
            admin.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive.",
            )

        admin.last_login_at = datetime.now(timezone.utc)

        session.add(admin)
        session.commit()

        access_token = create_access_token(
            {
                "sub": str(admin.admin_uuid),
                "role": "admin",
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }


# ============================================================
# GET CURRENT ADMIN DETAILS
# ============================================================

def get_admin_by_uuid(
    admin_uuid: str,
) -> dict:
    """Return the public profile of an active administrator."""

    try:
        validated_uuid = UUID(str(admin_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin identity.",
        )

    with get_session_context() as session:
        statement = select(Admin).where(
            Admin.admin_uuid == validated_uuid
        )

        admin = session.exec(statement).first()

        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account no longer exists.",
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive.",
            )

        return {
            "admin_uuid": str(admin.admin_uuid),
            "admin_name": admin.admin_name,
            "email": admin.email,
            "is_active": admin.is_active,
            "last_login_at": admin.last_login_at,
        }


# ============================================================
# CUSTOMER RESPONSE HELPER
# ============================================================

def _customer_to_dict(
    customer: Customer,
) -> dict:
    """Return safe customer details without credentials."""

    return {
        "customer_id": customer.customer_id,
        "customer_uuid": str(customer.customer_uuid),
        "customer_name": customer.customer_name,
        "phone": customer.phone,
        "city": customer.city,
        "area": customer.area,
        "pincode": customer.pincode,
        "last_login_at": customer.last_login_at,
    }


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

def get_all_customers() -> list[dict]:
    """Return all customers for the Admin dashboard."""

    with get_session_context() as session:
        statement = select(Customer).order_by(
            Customer.customer_id
        )

        customers = session.exec(statement).all()

        return [
            _customer_to_dict(customer)
            for customer in customers
        ]


# ============================================================
# GET ONE CUSTOMER
# ============================================================

def get_customer_by_uuid(
    customer_uuid: str,
) -> dict:
    """Return one customer's public details."""

    try:
        validated_uuid = UUID(str(customer_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid customer UUID.",
        )

    with get_session_context() as session:
        statement = select(Customer).where(
            Customer.customer_uuid == validated_uuid
        )

        customer = session.exec(statement).first()

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        return _customer_to_dict(customer)


# ============================================================
# GET A CUSTOMER'S SERVICE REQUESTS
# ============================================================

def get_customer_service_requests(
    customer_uuid: str,
) -> list[dict]:
    """Return service requests belonging to one customer."""

    try:
        validated_uuid = UUID(str(customer_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid customer UUID.",
        )

    with get_session_context() as session:
        customer_statement = select(Customer).where(
            Customer.customer_uuid == validated_uuid
        )

        customer = session.exec(
            customer_statement
        ).first()

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        statement = (
            select(
                ServiceRequest,
                Skill,
                Technician,
            )
            .join(
                Skill,
                ServiceRequest.skill_id == Skill.skill_id,
            )
            .outerjoin(
                Technician,
                ServiceRequest.assigned_technician_id
                == Technician.technician_id,
            )
            .where(
                ServiceRequest.customer_id
                == customer.customer_id,
            )
            .order_by(
                ServiceRequest.request_date.desc(),
            )
        )

        results = session.exec(statement).all()

        service_requests = []

        for service_request, skill, technician in results:
            service_requests.append(
                {
                    "request_uuid": str(
                        service_request.request_uuid
                    ),
                    "service": skill.skill_name,
                    "problem_description": (
                        service_request.problem_description
                    ),
                    "priority": service_request.priority,
                    "status": service_request.status,
                    "request_date": (
                        service_request.request_date
                    ),
                    "technician": (
                        {
                            "technician_uuid": str(
                                technician.technician_uuid
                            ),
                            "technician_name": (
                                technician.technician_name
                            ),
                        }
                        if technician
                        else None
                    ),
                }
            )

        return service_requests


# ============================================================
# TECHNICIAN RESPONSE HELPER
# ============================================================

def _technician_to_dict(
    technician: Technician,
) -> dict:
    """Return safe technician details without credentials."""

    return {
        "technician_id": technician.technician_id,
        "technician_uuid": str(technician.technician_uuid),
        "technician_name": technician.technician_name,
        "phone": technician.phone,
        "city": technician.city,
        "area": technician.area,
        "pincode": technician.pincode,
        "availability": technician.availability,
        "workload": technician.workload,
        "rating": technician.rating,
        "approval_status": technician.approval_status,
        "last_login_at": technician.last_login_at,
    }


# ============================================================
# GET ALL TECHNICIANS
# ============================================================

def get_all_technicians() -> list[dict]:
    """Return all technicians for the Admin dashboard."""

    with get_session_context() as session:
        statement = select(Technician).order_by(
            Technician.technician_id
        )

        technicians = session.exec(statement).all()

        return [
            _technician_to_dict(technician)
            for technician in technicians
        ]


# ============================================================
# GET PENDING TECHNICIANS
# ============================================================

def get_pending_technicians() -> list[dict]:
    """Return technicians awaiting Admin approval."""

    with get_session_context() as session:
        statement = (
            select(Technician)
            .where(
                Technician.approval_status == "Pending"
            )
            .order_by(Technician.technician_id)
        )

        technicians = session.exec(statement).all()

        return [
            _technician_to_dict(technician)
            for technician in technicians
        ]


# ============================================================
# APPROVE OR REJECT A TECHNICIAN
# ============================================================

def update_technician_approval(
    technician_uuid: str,
    approval_status: str,
) -> dict:
    """
    Approve or reject a technician account.

    Approval requires at least one verified skill.
    Rejection does not require skill verification.
    """

    normalized_status = str(approval_status).strip().title()

    if normalized_status not in {"Approved", "Rejected"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid approval status. "
                "Allowed values are Approved and Rejected."
            ),
        )

    try:
        validated_uuid = UUID(str(technician_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid technician UUID.",
        )

    with get_session_context() as session:
        statement = select(Technician).where(
            Technician.technician_uuid == validated_uuid
        )

        technician = session.exec(statement).first()

        if technician is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found.",
            )

        # Require at least one verified skill before approval.
        if normalized_status == "Approved":
            verified_skill_statement = (
                select(TechnicianSkill)
                .where(
                    TechnicianSkill.technician_id
                    == technician.technician_id,
                    TechnicianSkill.is_verified.is_(True),
                )
            )

            verified_skill = session.exec(
                verified_skill_statement
            ).first()

            if verified_skill is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Cannot approve this technician. "
                        "At least one skill must be verified first."
                    ),
                )

        technician.approval_status = normalized_status

        session.add(technician)
        session.commit()
        session.refresh(technician)

        return {
            "message": (
                f"Technician {normalized_status.lower()} successfully."
            ),
            "technician": _technician_to_dict(technician),
        }


# ============================================================
# TECHNICIAN SKILL RESPONSE HELPER
# ============================================================

def _technician_skill_to_dict(
    technician: Technician,
    technician_skill: TechnicianSkill,
    skill: Skill,
) -> dict:
    """Build a safe response for a technician's submitted skill."""

    return {
        "technician_id": technician.technician_id,
        "technician_uuid": str(technician.technician_uuid),
        "technician_name": technician.technician_name,
        "technician_approval_status": technician.approval_status,
        "skill_id": skill.skill_id,
        "skill_uuid": str(skill.skill_uuid),
        "skill_name": skill.skill_name,
        "category": skill.category,
        "difficulty_level": skill.difficulty_level,
        "estimated_duration": skill.estimated_duration,
        "description": skill.description,
        "experience_years": technician_skill.experience_years,
        "expertise_level": technician_skill.expertise_level,
        "is_verified": technician_skill.is_verified,
    }


# ============================================================
# GET ALL TECHNICIAN SKILLS
# ============================================================

def get_all_technician_skills() -> list[dict]:
    """Return all submitted technician skills for Admin review."""

    with get_session_context() as session:
        statement = (
            select(Technician, TechnicianSkill, Skill)
            .join(
                TechnicianSkill,
                Technician.technician_id
                == TechnicianSkill.technician_id,
            )
            .join(
                Skill,
                TechnicianSkill.skill_id == Skill.skill_id,
            )
            .order_by(
                Technician.technician_id,
                Skill.skill_name,
            )
        )

        results = session.exec(statement).all()

        return [
            _technician_skill_to_dict(
                technician,
                technician_skill,
                skill,
            )
            for technician, technician_skill, skill in results
        ]


# ============================================================
# GET PENDING TECHNICIAN SKILLS
# ============================================================

def get_pending_technician_skills() -> list[dict]:
    """Return technician skills that have not been verified."""

    with get_session_context() as session:
        statement = (
            select(Technician, TechnicianSkill, Skill)
            .join(
                TechnicianSkill,
                Technician.technician_id
                == TechnicianSkill.technician_id,
            )
            .join(
                Skill,
                TechnicianSkill.skill_id == Skill.skill_id,
            )
            .where(
                TechnicianSkill.is_verified.is_(False)
            )
            .order_by(
                Technician.technician_id,
                Skill.skill_name,
            )
        )

        results = session.exec(statement).all()

        return [
            _technician_skill_to_dict(
                technician,
                technician_skill,
                skill,
            )
            for technician, technician_skill, skill in results
        ]


# ============================================================
# VERIFY OR UNVERIFY A TECHNICIAN SKILL
# ============================================================

def update_technician_skill_verification(
    technician_uuid: str,
    skill_id: int,
    is_verified: bool,
) -> dict:
    """
    Verify a submitted skill or remove its verification.

    Only an Admin-protected API endpoint should call this function.
    """

    if not isinstance(is_verified, bool):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="is_verified must be a boolean.",
        )

    if skill_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="skill_id must be a positive integer.",
        )

    try:
        validated_uuid = UUID(str(technician_uuid))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid technician UUID.",
        )

    with get_session_context() as session:
        technician_statement = select(Technician).where(
            Technician.technician_uuid == validated_uuid
        )

        technician = session.exec(
            technician_statement
        ).first()

        if technician is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found.",
            )

        skill_statement = select(Skill).where(
            Skill.skill_id == skill_id
        )

        skill = session.exec(skill_statement).first()

        if skill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found.",
            )

        association_statement = select(
            TechnicianSkill
        ).where(
            TechnicianSkill.technician_id
            == technician.technician_id,
            TechnicianSkill.skill_id == skill_id,
        )

        technician_skill = session.exec(
            association_statement
        ).first()

        if technician_skill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This skill is not associated with the technician.",
            )

        technician_skill.is_verified = is_verified

        session.add(technician_skill)
        session.commit()
        session.refresh(technician_skill)

        return {
            "message": (
                "Technician skill verified successfully."
                if is_verified
                else "Technician skill verification removed."
            ),
            "technician": {
                "technician_uuid": str(technician.technician_uuid),
                "technician_name": technician.technician_name,
                "approval_status": technician.approval_status,
            },
            "skill": {
                "skill_id": skill.skill_id,
                "skill_uuid": str(skill.skill_uuid),
                "skill_name": skill.skill_name,
                "category": skill.category,
                "experience_years": technician_skill.experience_years,
                "expertise_level": technician_skill.expertise_level,
                "is_verified": technician_skill.is_verified,
            },
        }

# ============================================================
# ADMIN REPORT: CUSTOMER REPORT
# ============================================================

def get_customer_report() -> list[dict]:
    """Return customer details and their service-request statistics."""

    with get_session_context() as session:
        customers = session.exec(
            select(Customer).order_by(Customer.customer_id)
        ).all()

        report = []

        for customer in customers:
            requests = session.exec(
                select(ServiceRequest).where(
                    ServiceRequest.customer_id == customer.customer_id
                )
            ).all()

            total_requests = len(requests)
            completed_requests = sum(
                1 for request in requests
                if request.status == "COMPLETED"
            )
            outstanding_requests = sum(
                1 for request in requests
                if request.status not in {"COMPLETED", "CANCELLED"}
            )

            report.append({
                **_customer_to_dict(customer),
                "total_requests": total_requests,
                "completed_requests": completed_requests,
                "outstanding_requests": outstanding_requests,
            })

        return report


# ============================================================
# ADMIN REPORT: TECHNICIAN REPORT
# ============================================================

def get_technician_report() -> list[dict]:
    """Return technician details and service-request statistics."""

    with get_session_context() as session:
        technicians = session.exec(
            select(Technician).order_by(
                Technician.technician_id
            )
        ).all()

        report = []

        for technician in technicians:
            requests = session.exec(
                select(ServiceRequest).where(
                    ServiceRequest.assigned_technician_id
                    == technician.technician_id
                )
            ).all()

            assigned_requests = len(requests)
            completed_requests = sum(
                1 for request in requests
                if request.status == "COMPLETED"
            )

            verified_skills = session.exec(
                select(TechnicianSkill).where(
                    TechnicianSkill.technician_id
                    == technician.technician_id,
                    TechnicianSkill.is_verified.is_(True),
                )
            ).all()

            technician_data = _technician_to_dict(technician)

            technician_data.update({
                "assigned_requests": assigned_requests,
                "completed_requests": completed_requests,
                "verified_skills_count": len(verified_skills),
            })

            report.append(technician_data)

        return report


# ============================================================
# ADMIN REPORT: DASHBOARD SUMMARY
# ============================================================

def get_admin_report_summary() -> dict:
    """Return overall customer, technician, and request statistics."""

    with get_session_context() as session:
        customers = session.exec(
            select(Customer)
        ).all()

        technicians = session.exec(
            select(Technician)
        ).all()

        service_requests = session.exec(
            select(ServiceRequest)
        ).all()

        pending_technicians = sum(
            1 for technician in technicians
            if technician.approval_status == "Pending"
        )

        approved_technicians = sum(
            1 for technician in technicians
            if technician.approval_status == "Approved"
        )

        rejected_technicians = sum(
            1 for technician in technicians
            if technician.approval_status == "Rejected"
        )

        requests_by_status = {}

        for service_request in service_requests:
            request_status = service_request.status

            requests_by_status[request_status] = (
                requests_by_status.get(request_status, 0) + 1
            )

        return {
            "total_customers": len(customers),
            "total_technicians": len(technicians),
            "pending_technicians": pending_technicians,
            "approved_technicians": approved_technicians,
            "rejected_technicians": rejected_technicians,
            "total_service_requests": len(service_requests),
            "completed_requests": sum(
                1 for request in service_requests
                if request.status == "COMPLETED"
            ),
            "requests_by_status": requests_by_status,
        }
