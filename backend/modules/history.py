from  sqlmodel import select

from Orm.database import get_session_context
from Orm.service_history import ServiceHistory


def add_history(
    request_id,
    old_status,
    new_status,
    remarks
):

    try:

        with get_session_context() as session:

            history = ServiceHistory(
                request_id=request_id,
                old_status=old_status,
                new_status=new_status,
                remarks=remarks
            )

            session.add(history)

            session.commit()

    except Exception as err:

        print(
            "\nHistory Error :",
            err
        )


def add_history_to_session(
    session,
    request_id,
    old_status,
    new_status,
    remarks
):

    history = ServiceHistory(
        request_id=request_id,
        old_status=old_status,
        new_status=new_status,
        remarks=remarks
    )

    session.add(history)


def view_service_history():

    try:

        request_id = int(
            input("\nEnter Request ID : ")
        )

        with get_session_context() as session:

            statement = (
                select(ServiceHistory)
                .where(
                    ServiceHistory.request_id
                    == request_id
                )
                .order_by(
                    ServiceHistory.updated_time
                )
            )

            history = (
                session.exec(statement).all()
            )

            if not history:

                print(
                    "\nNo Service History Found."
                )

                return

            print(
                "\n========== SERVICE TIMELINE ==========\n"
            )

            for record in history:

                print(
                    f"History ID   : "
                    f"{record.history_id}"
                )

                print(
                    f"History UUID : "
                    f"{record.history_uuid}"
                )

                print(
                    "Status Changed"
                )

                print(
                    f"{record.old_status}  →  "
                    f"{record.new_status}"
                )

                print(
                    f"Time    : "
                    f"{record.updated_time.strftime('%d-%m-%Y %I:%M:%S %p')}"
                )

                print(
                    f"Remarks : "
                    f"{record.remarks}"
                )

                print(
                    "------------------------------------------"
                )

    except ValueError:

        print(
            "\nInvalid Request ID."
        )

    except Exception as err:

        print(
            "\nError :",
            err
        )