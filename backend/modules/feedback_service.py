from  sqlmodel import select

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.feedback import Feedback
from Orm.service_request import ServiceRequest
from Orm.technician import Technician


class CustomerNotFoundError(Exception):
    pass


class ServiceRequestNotFoundError(Exception):
    pass


class UnauthorizedFeedbackError(Exception):
    pass


class IncompleteServiceError(Exception):
    pass


class NoTechnicianAssignedError(Exception):
    pass


class FeedbackAlreadyExistsError(Exception):
    pass


class TechnicianNotFoundError(Exception):
    pass


class InvalidUserRoleError(Exception):
    pass


def create_feedback(
    customer_uuid,
    request_uuid,
    rating,
    comments
):
    with get_session_context() as session:

        # Find customer
        customer = session.exec(
            select(Customer).where(
                Customer.customer_uuid == customer_uuid
            )
        ).first()

        if not customer:
            raise CustomerNotFoundError(
                "Customer not found."
            )

        # Find service request
        service_request = session.exec(
            select(ServiceRequest).where(
                ServiceRequest.request_uuid == request_uuid
            )
        ).first()

        if not service_request:
            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        # Check ownership
        if service_request.customer_id != customer.customer_id:
            raise UnauthorizedFeedbackError(
                "You are not allowed to give feedback "
                "for this service request."
            )

        # Feedback only after completion
        if service_request.status != "COMPLETED":
            raise IncompleteServiceError(
                "Feedback can only be submitted "
                "after the service is completed."
            )

        # Technician must be assigned
        if not service_request.assigned_technician_id:
            raise NoTechnicianAssignedError(
                "No technician is assigned to this request."
            )

        # Prevent duplicate feedback
        existing_feedback = session.exec(
            select(Feedback).where(
                Feedback.request_id == service_request.request_id
            )
        ).first()

        if existing_feedback:
            raise FeedbackAlreadyExistsError(
                "Feedback has already been submitted."
            )

        # Find technician
        technician = session.get(
            Technician,
            service_request.assigned_technician_id
        )

        if not technician:
            raise TechnicianNotFoundError(
                "Technician not found."
            )

        # Create feedback
        feedback = Feedback(
            request_id=service_request.request_id,
            customer_id=customer.customer_id,
            technician_id=technician.technician_id,
            rating=rating,
            comments=(
                comments.strip()
                if comments
                else None
            )
        )

        session.add(feedback)
        session.commit()
        session.refresh(feedback)

        # Get all feedback for technician
        feedback_records = session.exec(
            select(Feedback).where(
                Feedback.technician_id
                == technician.technician_id
            )
        ).all()

        total_rating = sum(
            float(record.rating)
            for record in feedback_records
            if record.rating is not None
        )

        rating_count = len(
            [
                record
                for record in feedback_records
                if record.rating is not None
            ]
        )

        # Update technician average rating
        if rating_count > 0:
            technician.rating = round(
                total_rating / rating_count,
                2
            )

        session.add(technician)
        session.commit()
        session.refresh(technician)

        return {
            "message": "Feedback submitted successfully.",
            "feedback_uuid": feedback.feedback_uuid,
            "request_uuid": service_request.request_uuid,
            "rating": feedback.rating,
            "comments": feedback.comments,
            "technician": {
                "technician_uuid": technician.technician_uuid,
                "technician_name": technician.technician_name,
                "rating": technician.rating
            }
        }


def get_feedback(
    user_uuid,
    role,
    request_uuid
):
    with get_session_context() as session:

        # Find service request
        service_request = session.exec(
            select(ServiceRequest).where(
                ServiceRequest.request_uuid == request_uuid
            )
        ).first()

        if not service_request:
            raise ServiceRequestNotFoundError(
                "Service request not found."
            )

        # Customer authorization
        if role == "customer":

            customer = session.exec(
                select(Customer).where(
                    Customer.customer_uuid == user_uuid
                )
            ).first()

            if not customer:
                raise CustomerNotFoundError(
                    "Customer not found."
                )

            if service_request.customer_id != customer.customer_id:
                raise UnauthorizedFeedbackError(
                    "You are not allowed to view "
                    "this feedback."
                )

        # Technician authorization
        elif role == "technician":

            technician = session.exec(
                select(Technician).where(
                    Technician.technician_uuid == user_uuid
                )
            ).first()

            if not technician:
                raise TechnicianNotFoundError(
                    "Technician not found."
                )

            if (
                service_request.assigned_technician_id
                != technician.technician_id
            ):
                raise UnauthorizedFeedbackError(
                    "You are not allowed to view "
                    "this feedback."
                )

        else:
            raise InvalidUserRoleError(
                "Invalid user role."
            )

        # Find feedback
        feedback = session.exec(
            select(Feedback).where(
                Feedback.request_id
                == service_request.request_id
            )
        ).first()

        if not feedback:
            return {
                "request_uuid": service_request.request_uuid,
                "message": "No feedback found.",
                "feedback": None
            }

        # Find technician
        technician = session.get(
            Technician,
            feedback.technician_id
        )

        if not technician:
            raise TechnicianNotFoundError(
                "Technician not found."
            )

        return {
            "request_uuid": service_request.request_uuid,
            "feedback": {
                "feedback_uuid": feedback.feedback_uuid,
                "rating": feedback.rating,
                "comments": feedback.comments,
                "feedback_date": feedback.feedback_date
            },
            "technician": {
                "technician_uuid": technician.technician_uuid,
                "technician_name": technician.technician_name,
                "rating": technician.rating
            }
        }