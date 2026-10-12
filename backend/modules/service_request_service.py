from sqlmodel import select

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.skills import Skill
from Orm.service_request import ServiceRequest
from Orm.service_history import ServiceHistory
from Orm.technician import Technician

from modules.chroma_service import find_service_by_problem
from modules.matching import find_best_technician
from modules.service_request import has_pending_service_request


# ============================================================
# SERVICE LAYER EXCEPTIONS
# ============================================================

class ServiceRequestNotFoundError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class TechnicianNotFoundError(Exception):
    pass


class UnauthorizedServiceRequestError(Exception):
    pass


class DuplicateServiceRequestError(Exception):
    pass


class InvalidServiceRequestStatusError(Exception):
    pass


# ============================================================
# DETECT SERVICE
# ============================================================

def detect_service(
    customer_uuid,
    problem_description
):

    # ========================================================
    # VALIDATE PROBLEM DESCRIPTION
    # ========================================================

    problem_description = problem_description.strip()

    if not problem_description:

        raise ValueError(
            "Problem description cannot be empty."
        )

    # ========================================================
    # FIND CUSTOMER
    # ========================================================

    with get_session_context() as session:

        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid
                == customer_uuid
            )
        ).first()

        if not customer:

            raise CustomerNotFoundError(
                "Customer not found."
            )

        # ====================================================
        # FIND SERVICE USING CHROMA
        # ====================================================

        detection = find_service_by_problem(
            problem_description
        )

        # ====================================================
        # SERVICE DETECTED
        # ====================================================

        if detection:

            return {
                "skill_id": detection["skill_id"],
                "skill_name": detection["skill_name"],
                "category": detection["category"],
                "match_type": detection.get("match_type"),
                "distance": detection.get("distance"),
                "available_services": []
            }

        # ====================================================
        # SERVICE NOT DETECTED
        #
        # Match the CLI behavior:
        # show all available services so the customer
        # can manually select one.
        # ====================================================

        skills = session.exec(
            select(Skill).order_by(
                Skill.skill_id
            )
        ).all()

        available_services = []

        for skill in skills:

            available_services.append(
                {
                    "skill_id": skill.skill_id,
                    "skill_name": skill.skill_name
                }
            )

        return {
            "skill_id": None,
            "skill_name": None,
            "category": None,
            "match_type": None,
            "distance": None,
            "available_services": available_services
        }


# ============================================================
# CREATE SERVICE REQUEST
# ============================================================

def create_service_request(
    customer_uuid,
    problem_description,
    skill_id,
    priority
):

    # ========================================================
    # VALIDATE SKILL ID
    # ========================================================

    if not skill_id:

        raise ValueError(
            "A service must be selected before "
            "creating the service request."
        )

    # ========================================================
    # VALIDATE PROBLEM DESCRIPTION
    # ========================================================

    problem_description = problem_description.strip()

    if not problem_description:

        raise ValueError(
            "Problem description cannot be empty."
        )

    # ========================================================
    # VALIDATE PRIORITY
    # ========================================================

    priority = priority.strip().title()

    if priority not in [
        "Low",
        "Medium",
        "High"
    ]:

        raise ValueError(
            "Priority must be Low, Medium or High."
        )

    # ========================================================
    # FIND CUSTOMER
    # ========================================================

    with get_session_context() as session:

        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid
                == customer_uuid
            )
        ).first()

        if not customer:

            raise CustomerNotFoundError(
                "Customer not found."
            )

        # ====================================================
        # FIND SELECTED SKILL
        # ====================================================

        selected_skill = session.get(
            Skill,
            skill_id
        )

        if not selected_skill:

            raise ValueError(
                "Service not found."
            )

        selected_skill_id = (
            selected_skill.skill_id
        )

        selected_skill_name = (
            selected_skill.skill_name
        )

        # ====================================================
        # CHECK EXISTING PENDING REQUEST
        # ====================================================

        if has_pending_service_request(
            session,
            customer.customer_id,
            selected_skill_id
        ):

            raise DuplicateServiceRequestError(
                f"You already have a pending "
                f"{selected_skill_name} service request. "
                f"Please wait until the existing request "
                f"is completed before booking the same "
                f"service again."
            )

        # ====================================================
        # CREATE SERVICE REQUEST
        # ====================================================

        service_request = ServiceRequest(

            customer_id=customer.customer_id,

            skill_id=selected_skill_id,

            problem_description=(
                problem_description
            ),

            priority=priority,

            status="OPEN"
        )

        session.add(
            service_request
        )

        session.commit()

        session.refresh(
            service_request
        )

        request_id = service_request.request_id

        request_uuid = service_request.request_uuid

    # ========================================================
    # FIND BEST TECHNICIAN
    # ========================================================

    technician_id = find_best_technician(
        request_id
    )

    technician_uuid = None
    technician_name = None

    if technician_id:

        with get_session_context() as session:

            assigned_technician = session.get(
                Technician,
                technician_id
            )

            if assigned_technician:

                technician_uuid = (
                    assigned_technician.technician_uuid
                )

                technician_name = (
                    assigned_technician.technician_name
                )

    # ========================================================
    # GET UPDATED REQUEST
    # ========================================================

    with get_session_context() as session:

        updated_request = session.get(
            ServiceRequest,
            request_id
        )

        if not updated_request:

            raise ServiceRequestNotFoundError(
                "Service request not found after creation."
            )

        request_status = (
            updated_request.status
        )

        request_priority = (
            updated_request.priority
        )

    # ========================================================
    # BUILD RESULT
    # ========================================================

    response = {

        "message": (
            "Service request created successfully."
        ),

        "request_uuid": request_uuid,

        "service": selected_skill_name,

        "priority": request_priority,

        "status": request_status
    }

    # ========================================================
    # TECHNICIAN INFORMATION
    # ========================================================

    if technician_uuid:

        response["technician"] = {

            "technician_uuid": technician_uuid,

            "technician_name": technician_name
        }

    else:

        response["technician"] = None

        response["message"] = (
            "Service request created, "
            "but no suitable technician is "
            "currently available."
        )

    return response


# ============================================================
# GET CUSTOMER SERVICE REQUESTS
# ============================================================

def get_customer_service_requests(
    customer_uuid
):

    with get_session_context() as session:

        # ====================================================
        # FIND CUSTOMER
        # ====================================================

        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid
                == customer_uuid
            )
        ).first()

        if not customer:

            raise CustomerNotFoundError(
                "Customer not found."
            )

        # ====================================================
        # GET REQUESTS
        # ====================================================

        statement = (
            select(
                ServiceRequest,
                Skill,
                Technician
            )
            .join(
                Skill,
                ServiceRequest.skill_id
                == Skill.skill_id
            )
            .outerjoin(
                Technician,
                ServiceRequest.assigned_technician_id
                == Technician.technician_id
            )
            .where(
                ServiceRequest.customer_id
                == customer.customer_id
            )
            .order_by(
                ServiceRequest.request_date.desc()
            )
        )

        results = session.exec(
            statement
        ).all()

        service_requests = []

        for service_request, skill, technician in results:

            request_data = {

                "request_uuid": (
                    service_request.request_uuid
                ),

                "service": skill.skill_name,

                "problem_description": (
                    service_request.problem_description
                ),

                "priority": (
                    service_request.priority
                ),

                "status": (
                    service_request.status
                ),

                "request_date": (
                    service_request.request_date
                ),

                "technician": None
            }

            if technician:

                request_data["technician"] = {

                    "technician_uuid": (
                        technician.technician_uuid
                    ),

                    "technician_name": (
                        technician.technician_name
                    )
                }

            service_requests.append(
                request_data
            )

        return service_requests


# ============================================================
# GET ONE CUSTOMER SERVICE REQUEST
# ============================================================

def get_customer_service_request(
    customer_uuid,
    request_uuid
):

    with get_session_context() as session:

        # ====================================================
        # FIND CUSTOMER
        # ====================================================

        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid
                == customer_uuid
            )
        ).first()

        if not customer:

            raise CustomerNotFoundError(
                "Customer not found."
            )

        # ====================================================
        # FIND REQUEST
        # ====================================================

        statement = (
            select(
                ServiceRequest,
                Skill,
                Technician
            )
            .join(
                Skill,
                ServiceRequest.skill_id
                == Skill.skill_id
            )
            .outerjoin(
                Technician,
                ServiceRequest.assigned_technician_id
                == Technician.technician_id
            )
            .where(
                ServiceRequest.request_uuid
                == request_uuid,

                ServiceRequest.customer_id
                == customer.customer_id
            )
        )

        result = session.exec(
            statement
        ).first()

        if not result:

            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        service_request, skill, technician = result

        request_data = {

            "request_uuid": (
                service_request.request_uuid
            ),

            "service": skill.skill_name,

            "problem_description": (
                service_request.problem_description
            ),

            "priority": (
                service_request.priority
            ),

            "status": (
                service_request.status
            ),

            "request_date": (
                service_request.request_date
            ),

            "technician": None
        }

        if technician:

            request_data["technician"] = {

                "technician_uuid": (
                    technician.technician_uuid
                ),

                "technician_name": (
                    technician.technician_name
                )
            }

        return request_data


# ============================================================
# GET SERVICE REQUEST HISTORY
# ============================================================

def get_service_request_history(
    customer_uuid,
    request_uuid
):

    with get_session_context() as session:

        # ====================================================
        # FIND CUSTOMER
        # ====================================================

        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid
                == customer_uuid
            )
        ).first()

        if not customer:

            raise CustomerNotFoundError(
                "Customer not found."
            )

        # ====================================================
        # FIND SERVICE REQUEST
        # ====================================================

        service_request = session.exec(
            select(ServiceRequest).where(
                ServiceRequest.request_uuid
                == request_uuid,

                ServiceRequest.customer_id
                == customer.customer_id
            )
        ).first()

        if not service_request:

            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        # ====================================================
        # GET HISTORY
        # ====================================================

        history_records = session.exec(
            select(ServiceHistory)
            .where(
                ServiceHistory.request_id
                == service_request.request_id
            )
            .order_by(
                ServiceHistory.updated_time.asc()
            )
        ).all()

        history = []

        for record in history_records:

            history.append(
                {
                    "old_status": record.old_status,
                    "new_status": record.new_status,
                    "remarks": record.remarks,
                    "updated_time": record.updated_time
                }
            )

        return {

            "request_uuid": (
                service_request.request_uuid
            ),

            "count": len(history),

            "history": history
        }


# ============================================================
# UPDATE SERVICE REQUEST STATUS
# ============================================================

def update_service_request_status(
    technician_uuid,
    request_uuid,
    requested_status,
    remarks
):

    # ========================================================
    # NORMALIZE STATUS
    # ========================================================

    requested_status = (
        requested_status.strip().upper()
    )

    if requested_status == "IN_PROGRESS":

        new_status = "IN PROGRESS"

    elif requested_status == "IN PROGRESS":

        new_status = "IN PROGRESS"

    elif requested_status == "COMPLETED":

        new_status = "COMPLETED"

    else:

        raise InvalidServiceRequestStatusError(
            "Status must be IN_PROGRESS or COMPLETED."
        )

    with get_session_context() as session:

        # ====================================================
        # FIND TECHNICIAN
        # ====================================================

        technician = session.exec(
            select(Technician).where(
                Technician.technician_uuid
                == technician_uuid
            )
        ).first()

        if not technician:

            raise TechnicianNotFoundError(
                "Technician not found."
            )

        # ====================================================
        # FIND SERVICE REQUEST
        # ====================================================

        service_request = session.exec(
            select(ServiceRequest).where(
                ServiceRequest.request_uuid
                == request_uuid
            )
        ).first()

        if not service_request:

            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        # ====================================================
        # VERIFY ASSIGNMENT
        # ====================================================

        if (
            service_request.assigned_technician_id
            != technician.technician_id
        ):

            raise UnauthorizedServiceRequestError(
                "You are not assigned to this "
                "service request."
            )

        # ====================================================
        # OLD STATUS
        # ====================================================

        old_status = service_request.status

        # ====================================================
        # SAME STATUS
        # ====================================================

        if old_status == new_status:

            raise InvalidServiceRequestStatusError(
                "Service request already has this status."
            )

        # ====================================================
        # VALIDATE TRANSITION
        # ====================================================

        if (
            new_status == "IN PROGRESS"
            and old_status != "PENDING"
        ):

            raise InvalidServiceRequestStatusError(
                "Service request must be PENDING "
                "before it can be moved to IN PROGRESS."
            )

        if (
            new_status == "COMPLETED"
            and old_status != "IN PROGRESS"
        ):

            raise InvalidServiceRequestStatusError(
                "Service request must be IN PROGRESS "
                "before it can be completed."
            )

        # ====================================================
        # UPDATE STATUS
        # ====================================================

        service_request.status = new_status

        # ====================================================
        # WORKLOAD
        # ====================================================

        previous_workload = (
            technician.workload or 0
        )

        new_workload = previous_workload

        availability_changed = False

        # ====================================================
        # COMPLETED SERVICE
        # ====================================================

        if (
            new_status == "COMPLETED"
            and old_status != "COMPLETED"
        ):

            new_workload = max(
                previous_workload - 1,
                0
            )

            technician.workload = new_workload

            # =================================================
            # BUSY → AVAILABLE
            # =================================================

            if (
                technician.availability == "Busy"
                and new_workload < 5
            ):

                technician.availability = "Available"

                availability_changed = True

        # ====================================================
        # CREATE HISTORY
        # ====================================================

        history = ServiceHistory(
            request_id=service_request.request_id,
            old_status=old_status,
            new_status=new_status,
            remarks=(
                remarks.strip()
                if remarks
                else None
            )
        )

        session.add(history)

        # ====================================================
        # COMMIT
        # ====================================================

        session.commit()

        session.refresh(
            service_request
        )

        return {

            "message": (
                "Service request status "
                "updated successfully."
            ),

            "request_uuid": (
                service_request.request_uuid
            ),

            "old_status": old_status,

            "new_status": (
                service_request.status
            ),

            "remarks": history.remarks,

            "technician": {

                "technician_uuid": (
                    technician.technician_uuid
                ),

                "technician_name": (
                    technician.technician_name
                ),

                "previous_workload": (
                    previous_workload
                ),

                "new_workload": (
                    new_workload
                ),

                "availability": (
                    technician.availability
                ),

                "availability_changed": (
                    availability_changed
                )
            }
        }

# ============================================================
# GET CUSTOMER UUID FOR A SERVICE REQUEST
# ============================================================

def get_customer_uuid_for_request(request_uuid):
    """
    Return the customer UUID associated with a service request.
    Used to send notifications when a technician updates status.
    """

    with get_session_context() as session:

        service_request = session.exec(
            select(ServiceRequest).where(
                ServiceRequest.request_uuid == request_uuid
            )
        ).first()

        if not service_request:
            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        customer = session.get(
            Customer,
            service_request.customer_id
        )

        if not customer:
            raise CustomerNotFoundError(
                "Customer associated with this request was not found."
            )

        return customer.customer_uuid