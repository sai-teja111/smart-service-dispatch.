from  sqlmodel import select, func

from Orm.database import get_session_context
from Orm.customer import Customer
from Orm.technician import Technician
from Orm.skills import Skill
from Orm.service_request import ServiceRequest
from Orm.feedback import Feedback


def view_reports():

    try:

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

            print("\n")
            print("=" * 60)
            print("              SMART SERVICE REPORT")
            print("=" * 60)

            print("\nCUSTOMER & TECHNICIAN SUMMARY")
            print("-" * 60)

            print(
                f"Total Customers                 : "
                f"{total_customers}"
            )

            print(
                f"Total Technicians               : "
                f"{total_technicians}"
            )

            print(
                f"Total Services                  : "
                f"{total_services}"
            )

            print(
                f"Total Service Requests          : "
                f"{total_requests}"
            )

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

            print("\nSERVICE REQUEST STATUS")
            print("-" * 60)

            print(
                f"Open Requests                   : "
                f"{open_requests}"
            )

            print(
                f"Pending Requests                : "
                f"{pending_requests}"
            )

            print(
                f"In Progress Requests            : "
                f"{in_progress_requests}"
            )

            print(
                f"Completed Requests              : "
                f"{completed_requests}"
            )

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

            print("\nSERVICE PERFORMANCE")
            print("-" * 60)

            if most_requested:

                print(
                    f"Most Requested Service          : "
                    f"{most_requested[0]}"
                )

                print(
                    f"Total Requests for Service      : "
                    f"{most_requested[1]}"
                )

            else:

                print(
                    "Most Requested Service          : No data"
                )

                print(
                    "Total Requests for Service      : 0"
                )

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

            print("\nTECHNICIAN PERFORMANCE")
            print("-" * 60)

            if highest_rated:

                print(
                    f"Highest Rated Technician        : "
                    f"{highest_rated[0]}"
                )

                print(
                    f"Highest Rating                  : "
                    f"{highest_rated[1]}"
                )

            else:

                print(
                    "Highest Rated Technician        : No data"
                )

                print(
                    "Highest Rating                  : 0"
                )

            if average_rating is not None:

                print(
                    f"Average Technician Rating       : "
                    f"{round(float(average_rating), 1)}"
                )

            else:

                print(
                    "Average Technician Rating       : 0"
                )

            total_feedback = session.exec(
                select(func.count())
                .select_from (Feedback)
            ).one()

            average_feedback = session.exec(
                select(
                    func.avg(Feedback.rating)
                )
            ).one()

            print("\nFEEDBACK SUMMARY")
            print("-" * 60)

            print(
                f"Total Feedback                  : "
                f"{total_feedback}"
            )

            if average_feedback is not None:

                print(
                    f"Average Customer Rating        : "
                    f"{round(float(average_feedback), 1)}"
                )

            else:

                print(
                    "Average Customer Rating        : 0"
                )

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

            print("\nTECHNICIAN WORKLOAD")
            print("-" * 60)

            if technicians:

                print(
                    f"{'ID':<6}"
                    f"{'Technician':<22}"
                    f"{'Workload':<14}"
                    f"{'Rating':<10}"
                )

                print("-" * 60)

                for technician in technicians:

                    technician_id = technician[0]
                    technician_name = technician[1]
                    workload = technician[2]
                    rating = technician[3]

                    print(
                        f"{technician_id:<6}"
                        f"{technician_name:<22}"
                        f"{workload:<14}"
                        f"{rating:<10}"
                    )

            else:

                print("No technicians found.")

            print("\n" + "=" * 60)
            print("              END OF REPORT")
            print("=" * 60)

    except Exception as err:

        print(
            "\nReport Error :",
            err
        )