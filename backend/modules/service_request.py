from  sqlmodel import select

from Orm.database import get_session_context

from Orm.customer import Customer
from Orm.skills import Skill
from Orm.technician import Technician
from Orm.service_request import ServiceRequest

from modules.chroma_service import find_service_by_problem
from modules.skills import view_skills
from modules.matching import find_best_technician
from modules.history import add_history_to_session


# ============================================================
# CHECK PENDING SERVICE REQUEST
# ============================================================

def has_pending_service_request(
    session,
    customer_id,
    skill_id
):

    existing_request = session.exec(
        select(ServiceRequest).where(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.skill_id == skill_id,
            ServiceRequest.status == "PENDING"
        )
    ).first()

    return existing_request is not None

# ============================================================
# CREATE SERVICE REQUEST
# ============================================================

def create_service_request():

    try:

        customer_id = int(
            input("Enter Customer ID : ")
        )

        with get_session_context() as session:

            customer = session.get(
                Customer,
                customer_id
            )

            if not customer:

                print(
                    "\nCustomer not found."
                )

                print(
                    "Please register the customer first."
                )

                return

            print(
                f"\nWelcome, {customer.customer_name}"
            )

            problem_description = input(
                "\nDescribe your problem : "
            )

            if not problem_description.strip():

                print(
                    "\nProblem description cannot be empty."
                )

                return

            print(
                "\nAI is identifying the required service..."
            )

            detected_service = find_service_by_problem(
                problem_description
            )

            skill_id = None
            selected_skill_name = None

            # =================================================
            # AI DETECTED SERVICE
            # =================================================

            if detected_service:

                print(
                    "\n=========================================="
                )

                print(
                    "         SERVICE DETECTION"
                )

                print(
                    "=========================================="
                )

                print(
                    f"Detected Service : "
                    f"{detected_service['skill_name']}"
                )

                print(
                    f"Category         : "
                    f"{detected_service['category']}"
                )

                print(
                    f"Match Type       : "
                    f"{detected_service['match_type']}"
                )

                if "distance" in detected_service:

                    print(
                        f"Similarity       : "
                        f"{detected_service['distance']}"
                    )

                print(
                    "=========================================="
                )

                print(
                    "\nIs this the correct service?"
                )

                print(
                    "1. Yes"
                )

                print(
                    "2. No"
                )

                confirmation = input(
                    "Enter your choice (1-2): "
                )

                if confirmation == "1":

                    skill_id = detected_service[
                        "skill_id"
                    ]

                    selected_skill_name = (
                        detected_service[
                            "skill_name"
                        ]
                    )

                    print(
                        f"\nService selected: "
                        f"{selected_skill_name}"
                    )

                elif confirmation == "2":

                    print(
                        "\nPlease select the service manually."
                    )

                    view_skills()

                    skill_id = int(
                        input(
                            "\nEnter Service ID : "
                        )
                    )

                    skill = session.get(
                        Skill,
                        skill_id
                    )

                    if not skill:

                        print(
                            "\nInvalid Service ID."
                        )

                        return

                    selected_skill_name = (
                        skill.skill_name
                    )

                    print(
                        f"\nService selected: "
                        f"{selected_skill_name}"
                    )

                else:

                    print(
                        "\nInvalid choice."
                    )

                    return

            # =================================================
            # AI COULD NOT DETECT SERVICE
            # =================================================

            else:

                print(
                    "\nUnable to automatically identify "
                    "the required service."
                )

                print(
                    "\nPlease select the service manually."
                )

                view_skills()

                skill_id = int(
                    input(
                        "\nEnter Service ID : "
                    )
                )

                skill = session.get(
                    Skill,
                    skill_id
                )

                if not skill:

                    print(
                        "\nInvalid Service ID."
                    )

                    return

                selected_skill_name = (
                    skill.skill_name
                )

                print(
                    f"\nService selected: "
                    f"{selected_skill_name}"
                )
            # =================================================
            # CHECK FOR EXISTING PENDING REQUEST
            # =================================================

            if has_pending_service_request(
                session,
                customer_id,
                skill_id
            ):

                print(
                    "\n=========================================="
                )

                print(
                    "       SERVICE REQUEST ALREADY EXISTS"
                )

                print(
                    "=========================================="
                )

                print(
                    f"You already have a pending "
                    f"{selected_skill_name} service request."
                )

                print(
                    "Please wait until the existing request "
                    "is completed before booking the same service again."
                )

                print(
                    "=========================================="
                )

                return  

            # =================================================
            # PRIORITY
            # =================================================

            print(
                "\nSelect Priority Level:"
            )

            print(
                "1. Low"
            )

            print(
                "2. Medium"
            )

            print(
                "3. High"
            )

            priority_choice = input(
                "Enter your choice (1-3): "
            )

            if priority_choice == "1":

                priority = "Low"

            elif priority_choice == "2":

                priority = "Medium"

            elif priority_choice == "3":

                priority = "High"

            else:

                print(
                    "\nInvalid priority."
                )

                print(
                    "Defaulting to Low priority."
                )

                priority = "Low"

            # =================================================
            # CREATE SERVICE REQUEST
            # =================================================

            service_request = ServiceRequest(

                customer_id=customer_id,

                skill_id=skill_id,

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

            # =================================================
            # DISPLAY CREATED REQUEST
            # =================================================

            print(
                "\n=========================================="
            )

            print(
                "       SERVICE REQUEST CREATED"
            )

            print(
                "=========================================="
            )

            print(
                f"Request ID   : "
                f"{service_request.request_id}"
            )

            print(
                f"Request UUID : "
                f"{service_request.request_uuid}"
            )

            print(
                f"Service      : "
                f"{selected_skill_name}"
            )

            print(
                f"Priority     : "
                f"{priority}"
            )

            print(
                f"Status       : "
                f"{service_request.status}"
            )

            print(
                "=========================================="
            )

            # =================================================
            # FIND BEST TECHNICIAN
            # =================================================

            technician_id = find_best_technician(
                service_request.request_id
            )

            if technician_id:

                print(
                    "\nTechnician assigned successfully."
                )

            else:

                print(
                    "\nNo suitable technician is "
                    "currently available."
                )


    except ValueError:

        print(
            "\nInvalid input."
        )

        print(
            "Please enter valid numeric values."
        )


    except Exception as err:

        print(
            "\nService Request Error :",
            err
        )


# ============================================================
# VIEW SERVICE REQUESTS
# ============================================================

def view_service_requests():

    try:

        with get_session_context() as session:

            requests = session.exec(
                select(ServiceRequest)
                .order_by(
                    ServiceRequest.request_id
                )
            ).all()

            if not requests:

                print(
                    "\nNo Service Requests Found."
                )

                return

            print(
                "\n========== SERVICE REQUESTS =========="
            )

            for request in requests:

                customer = session.get(
                    Customer,
                    request.customer_id
                )

                skill = session.get(
                    Skill,
                    request.skill_id
                )

                technician = None

                if request.assigned_technician_id:

                    technician = session.get(
                        Technician,
                        request.assigned_technician_id
                    )

                print(
                    f"\nRequest ID          : "
                    f"{request.request_id}"
                )

                print(
                    f"Request UUID        : "
                    f"{request.request_uuid}"
                )

                print(
                    f"Customer            : "
                    f"{customer.customer_name if customer else 'Unknown'}"
                )

                print(
                    f"Service             : "
                    f"{skill.skill_name if skill else 'Unknown'}"
                )

                print(
                    f"Problem             : "
                    f"{request.problem_description}"
                )

                print(
                    f"Priority            : "
                    f"{request.priority}"
                )

                if technician:

                    print(
                        f"Assigned Technician : "
                        f"{technician.technician_name}"
                    )

                    print(
                        f"Technician UUID     : "
                        f"{technician.technician_uuid}"
                    )

                else:

                    print(
                        "Assigned Technician : "
                        "Not Assigned"
                    )

                print(
                    f"Status              : "
                    f"{request.status}"
                )

                print(
                    f"Request Date        : "
                    f"{request.request_date}"
                )

                print(
                    "------------------------------------------"
                )


    except Exception as err:

        print(
            "\nError :",
            err
        )


# ============================================================
# UPDATE SERVICE STATUS
# ============================================================

def update_service_status():

    try:

        request_id = int(
            input(
                "\nEnter Request ID : "
            )
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

            old_status = (
                service_request.status
            )

            technician_id = (
                service_request.assigned_technician_id
            )

            print(
                f"\nRequest UUID : "
                f"{service_request.request_uuid}"
            )

            print(
                f"Current Status : "
                f"{old_status}"
            )

            # =================================================
            # SELECT NEW STATUS
            # =================================================

            print(
                "\nSelect New Status"
            )

            print(
                "1. OPEN"
            )

            print(
                "2. PENDING"
            )

            print(
                "3. IN PROGRESS"
            )

            print(
                "4. COMPLETED"
            )

            choice = input(
                "Enter your choice (1-4): "
            )

            if choice == "1":

                new_status = "OPEN"

            elif choice == "2":

                new_status = "PENDING"

            elif choice == "3":

                new_status = "IN PROGRESS"

            elif choice == "4":

                new_status = "COMPLETED"

            else:

                print(
                    "\nInvalid Choice."
                )

                return

            # =================================================
            # SAME STATUS CHECK
            # =================================================

            if old_status == new_status:

                print(
                    "\nRequest is already in this status."
                )

                return

            # =================================================
            # REMARKS
            # =================================================

            remarks = input(
                "\nEnter Remarks : "
            )

            # =================================================
            # UPDATE STATUS
            # =================================================

            service_request.status = (
                new_status
            )

            # =================================================
            # HANDLE TECHNICIAN WORKLOAD
            # =================================================

            if (
                new_status == "COMPLETED"
                and old_status != "COMPLETED"
                and technician_id is not None
            ):

                technician = session.get(
                    Technician,
                    technician_id
                )

                if technician:

                    current_workload = (
                        technician.workload or 0
                    )

                    current_availability = (
                        technician.availability
                    )

                    new_workload = max(
                        current_workload - 1,
                        0
                    )

                    technician.workload = (
                        new_workload
                    )

                    if (
                        current_availability == "Busy"
                        and new_workload < 5
                    ):

                        technician.availability = (
                            "Available"
                        )

                        availability_changed = True

                    else:

                        availability_changed = False

                    print(
                        "\nTechnician Workload Updated"
                    )

                    print(
                        f"Previous Workload : "
                        f"{current_workload}"
                    )

                    print(
                        f"New Workload      : "
                        f"{new_workload}"
                    )

                    if availability_changed:

                        print(
                            "Availability      : Available"
                        )

                    elif current_availability == "Unavailable":

                        print(
                            "Availability      : Unavailable"
                        )

            # =================================================
            # ADD SERVICE HISTORY
            # =================================================

            add_history_to_session(

                session,

                request_id,

                old_status,

                new_status,

                remarks
            )

            # =================================================
            # COMMIT
            # =================================================

            session.commit()

            # =================================================
            # DISPLAY RESULT
            # =================================================

            print(
                "\n==================================="
            )

            print(
                "       SERVICE STATUS UPDATED"
            )

            print(
                "==================================="
            )

            print(
                f"Request ID   : "
                f"{request_id}"
            )

            print(
                f"Request UUID : "
                f"{service_request.request_uuid}"
            )

            print(
                f"Old Status   : "
                f"{old_status}"
            )

            print(
                f"New Status   : "
                f"{new_status}"
            )

            print(
                f"Remarks      : "
                f"{remarks}"
            )

            print(
                "==================================="
            )


    except ValueError:

        print(
            "\nInvalid Request ID. "
            "Please enter a number."
        )


    except Exception as err:

        print(
            "\nError :",
            err
        )