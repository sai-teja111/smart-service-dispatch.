from  sqlmodel import select, func

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.technician import Technician
from Orm.skills import Skill
from Orm.service_request import ServiceRequest
from Orm.feedback import Feedback


def get_reports():
    with get_session_context() as session:

        total_customers = session.exec(
            select(func.count())
            .select_from (Customer)
        ).one()

        total_technicians = session.exec(
            select(func.count())
            .select_from (Technician)
        ).one()

        total_services = session.exec(
            select(func.count())
            .select_from (Skill)
        ).one()

        total_requests = session.exec(
            select(func.count())
            .select_from (ServiceRequest)
        ).one()

        open_requests = session.exec(
            select(func.count())
            .select_from (ServiceRequest)
            .where(
                func.upper(ServiceRequest.status)
                == "OPEN"
            )
        ).one()

        pending_requests = session.exec(
            select(func.count())
            .select_from (ServiceRequest)
            .where(
                func.upper(ServiceRequest.status)
                == "PENDING"
            )
        ).one()

        in_progress_requests = session.exec(
            select(func.count())
            .select_from (ServiceRequest)
            .where(
                func.upper(ServiceRequest.status)
                == "IN PROGRESS"
            )
        ).one()

        completed_requests = session.exec(
            select(func.count())
            .select_from (ServiceRequest)
            .where(
                func.upper(ServiceRequest.status)
                == "COMPLETED"
            )
        ).one()

        most_requested = session.exec(
            select(
                Skill.skill_name,
                func.count(
                    ServiceRequest.request_id
                )
            )
            .join(
                ServiceRequest,
                ServiceRequest.skill_id
                == Skill.skill_id
            )
            .group_by(
                Skill.skill_id,
                Skill.skill_name
            )
            .order_by(
                func.count(
                    ServiceRequest.request_id
                ).desc()
            )
            .limit(1)
        ).first()

        highest_rated = session.exec(
            select(
                Technician.technician_name,
                Technician.rating
            )
            .where(
                Technician.rating.is_not(None)
            )
            .order_by(
                Technician.rating.desc()
            )
            .limit(1)
        ).first()

        average_rating = session.exec(
            select(
                func.avg(Technician.rating)
            )
            .where(
                Technician.rating > 0
            )
        ).one()

        total_feedback = session.exec(
            select(func.count())
            .select_from (Feedback)
        ).one()

        average_feedback = session.exec(
            select(
                func.avg(Feedback.rating)
            )
        ).one()

        technicians = session.exec(
            select(
                Technician.technician_id,
                Technician.technician_name,
                Technician.workload,
                Technician.rating
            )
            .order_by(
                Technician.workload.desc()
            )
        ).all()

        technician_workload = []

        for technician in technicians:

            technician_workload.append(
                {
                    "technician_id": technician[0],
                    "technician_name": technician[1],
                    "workload": technician[2],
                    "rating": technician[3]
                }
            )

        return {
            "customer_technician_summary": {
                "total_customers": total_customers,
                "total_technicians": total_technicians,
                "total_services": total_services,
                "total_service_requests": total_requests
            },

            "service_request_status": {
                "open_requests": open_requests,
                "pending_requests": pending_requests,
                "in_progress_requests": in_progress_requests,
                "completed_requests": completed_requests
            },

            "service_performance": {
                "most_requested_service": (
                    most_requested[0]
                    if most_requested
                    else None
                ),
                "total_requests_for_service": (
                    most_requested[1]
                    if most_requested
                    else 0
                )
            },

            "technician_performance": {
                "highest_rated_technician": (
                    highest_rated[0]
                    if highest_rated
                    else None
                ),
                "highest_rating": (
                    highest_rated[1]
                    if highest_rated
                    else 0
                ),
                "average_technician_rating": (
                    round(
                        float(average_rating),
                        1
                    )
                    if average_rating is not None
                    else 0
                )
            },

            "feedback_summary": {
                "total_feedback": total_feedback,
                "average_customer_rating": (
                    round(
                        float(average_feedback),
                        1
                    )
                    if average_feedback is not None
                    else 0
                )
            },

            "technician_workload": technician_workload
        }