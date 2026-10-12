from  sqlmodel import select

from Orm.database import get_session_context

from Orm.feedback import Feedback
from Orm.service_request import ServiceRequest
from Orm.customer import Customer
from Orm.technician import Technician


def add_feedback():

    try:

        request_id = int(
            input("\nEnter Request ID : ")
        )

        with get_session_context() as session:

            service_request = session.get(
                ServiceRequest,
                request_id
            )

            if not service_request:

                print(
                    "\nService Request Not Found."
                )

                return

            customer_id = (
                service_request.customer_id
            )

            technician_id = (
                service_request.assigned_technician_id
            )

            status = (
                service_request.status
            )

            customer = session.get(
                Customer,
                customer_id
            )

            technician = None

            if technician_id is not None:

                technician = session.get(
                    Technician,
                    technician_id
                )

            print(
                f"\nCustomer    : "
                f"{customer.customer_name if customer else 'Unknown'}"
            )

            print(
                f"Technician  : "
                f"{technician.technician_name if technician else 'None'}"
            )

            print(
                f"Status      : "
                f"{status}"
            )

            if status != "COMPLETED":

                print(
                    "\nFeedback can be given only after "
                    "the service is completed."
                )

                return

            if technician_id is None:

                print(
                    "\nNo technician was assigned "
                    "to this request."
                )

                return

            existing_feedback = session.exec(
                select(Feedback)
                .where(
                    Feedback.request_id
                    == request_id
                )
            ).first()

            if existing_feedback:

                print(
                    "\nFeedback has already been submitted "
                    "for this request."
                )

                return

            print(
                "\n========== GIVE FEEDBACK =========="
            )

            rating = float(
                input("Enter Rating (1-5) : ")
            )

            if rating < 1 or rating > 5:

                print(
                    "\nRating must be between 1 and 5."
                )

                return

            comments = input(
                "Enter Comments : "
            )

            feedback = Feedback(
                request_id=request_id,
                customer_id=customer_id,
                technician_id=technician_id,
                rating=rating,
                comments=comments
            )

            session.add(
                feedback
            )

            ratings = session.exec(
                select(Feedback.rating)
                .where(
                    Feedback.technician_id
                    == technician_id
                )
            ).all()

            rating_values = [
                float(value)
                for value in ratings
                if value is not None
            ]

            if rating_values:

                average_rating = round(
                    sum(rating_values)
                    / len(rating_values),
                    1
                )

            else:

                average_rating = rating

            technician.rating = (
                average_rating
            )

            session.commit()

            session.refresh(
                feedback
            )

            print(
                "\n========================================"
            )

            print(
                "     FEEDBACK SUBMITTED SUCCESSFULLY"
            )

            print(
                "========================================"
            )

            print(
                f"Feedback ID           : "
                f"{feedback.feedback_id}"
            )

            print(
                f"Feedback UUID         : "
                f"{feedback.feedback_uuid}"
            )

            print(
                f"Request ID            : "
                f"{request_id}"
            )

            print(
                f"Request UUID          : "
                f"{service_request.request_uuid}"
            )

            print(
                f"Technician            : "
                f"{technician.technician_name}"
            )

            print(
                f"Customer Rating       : "
                f"{rating}"
            )

            print(
                f"New Technician Rating : "
                f"{average_rating}"
            )

            print(
                f"Comments              : "
                f"{comments}"
            )

            print(
                "========================================"
            )

    except ValueError:

        print(
            "\nPlease enter valid numeric values."
        )

    except Exception as err:

        print(
            "\nFeedback Error :",
            err
        )


def view_feedback():

    try:

        with get_session_context() as session:

            feedbacks = session.exec(
                select(Feedback)
                .order_by(
                    Feedback.feedback_id
                )
            ).all()

            if not feedbacks:

                print(
                    "\nNo Feedback Found."
                )

                return

            print(
                "\n========== CUSTOMER FEEDBACK =========="
            )

            for feedback in feedbacks:

                customer = session.get(
                    Customer,
                    feedback.customer_id
                )

                technician = session.get(
                    Technician,
                    feedback.technician_id
                )

                print(
                    f"\nFeedback ID   : "
                    f"{feedback.feedback_id}"
                )

                print(
                    f"Feedback UUID : "
                    f"{feedback.feedback_uuid}"
                )

                print(
                    f"Request ID    : "
                    f"{feedback.request_id}"
                )

                print(
                    f"Customer      : "
                    f"{customer.customer_name if customer else 'Unknown'}"
                )

                print(
                    f"Technician    : "
                    f"{technician.technician_name if technician else 'Unknown'}"
                )

                print(
                    f"Rating        : "
                    f"{feedback.rating}"
                )

                print(
                    f"Comments      : "
                    f"{feedback.comments}"
                )

                print(
                    f"Date          : "
                    f"{feedback.feedback_date}"
                )

                print(
                    "------------------------------------------"
                )

    except Exception as err:

        print(
            "\nError :",
            err
        )