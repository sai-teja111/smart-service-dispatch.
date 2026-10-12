from  sqlmodel import select

from Orm.database import get_session_context
from Orm.service_request import ServiceRequest
from Orm.skills import Skill
from Orm.technician import Technician
from Orm.customer import Customer


# ============================================================
# GET TECHNICIAN ASSIGNED SERVICE REQUESTS
# ============================================================

def get_assigned_service_requests(technician_uuid):

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

            return None

        # ====================================================
        # GET ASSIGNED SERVICE REQUESTS
        # ====================================================

        statement = (
            select(
                ServiceRequest,
                Skill,
                Customer
            )
            .join(
                Skill,
                ServiceRequest.skill_id
                == Skill.skill_id
            )
            .join(
                Customer,
                ServiceRequest.customer_id
                == Customer.customer_id
            )
            .where(
                ServiceRequest.assigned_technician_id
                == technician.technician_id
            )
            .order_by(
                ServiceRequest.request_date.desc()
            )
        )

        results = session.exec(
            statement
        ).all()

        # ====================================================
        # BUILD RESPONSE DATA
        # ====================================================

        service_requests = []

        for service_request, skill, customer in results:

            request_data = {
                "request_uuid": service_request.request_uuid,
                "service": skill.skill_name,
                "problem_description": (
                    service_request.problem_description
                ),
                "priority": service_request.priority,
                "status": service_request.status,
                "request_date": service_request.request_date,
                "customer": {
                    "customer_uuid": customer.customer_uuid,
                    "customer_name": customer.customer_name,
                    "phone": customer.phone,
                    "city": customer.city,
                    "area": customer.area,
                    "pincode": customer.pincode
                }
            }

            service_requests.append(
                request_data
            )

        return service_requests


# ============================================================
# GET ONE TECHNICIAN ASSIGNED SERVICE REQUEST
# ============================================================

def get_assigned_service_request(
    technician_uuid,
    request_uuid
):

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

            return None

        # ====================================================
        # FIND ASSIGNED SERVICE REQUEST
        # ====================================================

        statement = (
            select(
                ServiceRequest,
                Skill,
                Customer
            )
            .join(
                Skill,
                ServiceRequest.skill_id
                == Skill.skill_id
            )
            .join(
                Customer,
                ServiceRequest.customer_id
                == Customer.customer_id
            )
            .where(
                ServiceRequest.request_uuid
                == request_uuid,
                ServiceRequest.assigned_technician_id
                == technician.technician_id
            )
        )

        result = session.exec(
            statement
        ).first()

        if not result:

            return None

        service_request, skill, customer = result

        # ====================================================
        # BUILD RESPONSE DATA
        # ====================================================

        return {
            "request_uuid": service_request.request_uuid,
            "service": skill.skill_name,
            "problem_description": (
                service_request.problem_description
            ),
            "priority": service_request.priority,
            "status": service_request.status,
            "request_date": service_request.request_date,
            "customer": {
                "customer_uuid": customer.customer_uuid,
                "customer_name": customer.customer_name,
                "phone": customer.phone,
                "city": customer.city,
                "area": customer.area,
                "pincode": customer.pincode
            }
        }