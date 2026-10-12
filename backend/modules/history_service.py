from  sqlmodel import select

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.service_request import ServiceRequest
from Orm.service_history import ServiceHistory
from Orm.technician import Technician


class ServiceRequestNotFoundError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class TechnicianNotFoundError(Exception):
    pass


class UnauthorizedServiceHistoryError(Exception):
    pass


class InvalidUserRoleError(Exception):
    pass


def get_service_history(request_uuid, user_uuid, role):
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
                raise UnauthorizedServiceHistoryError(
                    "You are not allowed to view "
                    "this service history."
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
                raise UnauthorizedServiceHistoryError(
                    "You are not allowed to view "
                    "this service history."
                )

        # Invalid role
        else:
            raise InvalidUserRoleError(
                "Invalid user role."
            )

        # Get service history
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

        # No history
        if not history_records:
            return {
                "request_uuid": service_request.request_uuid,
                "message": "No service history found.",
                "history": []
            }

        history = []

        for record in history_records:
            history.append(
                {
                    "old_status": record.old_status,
                    "new_status": record.new_status,
                    "updated_time": record.updated_time,
                    "remarks": record.remarks
                }
            )

        return {
            "request_uuid": service_request.request_uuid,
            "current_status": service_request.status,
            "count": len(history),
            "history": history
        }