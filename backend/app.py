from modules.customer import (
    register_customer,
    view_customers
)

from modules.technician import (
    register_technician,
    view_technicians,
    manage_technician_availability
)

from modules.service_request import (
    create_service_request,
    view_service_requests,
    update_service_status
)

from modules.history import (
    view_service_history
)

from modules.Feedback import (
    add_feedback,
    view_feedback
)

from modules.reports import (
    view_reports
)

from modules.help_contact import (
    help_contact
)

from Ai.ai_assistant import (
    ai_assistant
)

from  dotenv import load_dotenv

from menu import print_menu

from Orm.database import engine

from Orm.customer import Customer
from Orm.technician import Technician
from Orm.skills import Skill
from Orm.technician_skill import TechnicianSkill
from Orm.service_request import ServiceRequest
from Orm.assignment import Assignment
from Orm.service_history import ServiceHistory
from Orm.feedback import Feedback

from  sqlmodel import SQLModel

import Log_config as Log_config


load_dotenv()

logger = Log_config.log()

logger.info(
    "Application Started"
)

SQLModel.metadata.create_all(
    engine
)


while True:

    print_menu()

    option = input(
        "\nEnter your choice : "
    )

    if option == "1":

        logger.info(
            "Register Customer Selected"
        )

        print(
            "\n========== Register Customer ==========\n"
        )

        register_customer()

    elif option == "2":

        logger.info(
            "Register Technician Selected"
        )

        print(
            "\n========== Register Technician ==========\n"
        )

        register_technician()

    elif option == "3":

        logger.info(
            "View Customers Selected"
        )

        print(
            "\n========== View Customers ==========\n"
        )

        view_customers()

    elif option == "4":

        logger.info(
            "View Technicians Selected"
        )

        print(
            "\n========== View Technicians ==========\n"
        )

        view_technicians()

    elif option == "5":

        logger.info(
            "Create Service Request Selected"
        )

        print(
            "\n========== Create Service Request ==========\n"
        )

        create_service_request()

    elif option == "6":

        logger.info(
            "View Service Requests Selected"
        )

        print(
            "\n========== View Service Requests ==========\n"
        )

        view_service_requests()

    elif option == "7":

        logger.info(
            "Update Service Status Selected"
        )

        print(
            "\n========== Update Service Status ==========\n"
        )

        update_service_status()

    elif option == "8":

        logger.info(
            "View Service History Selected"
        )

        print(
            "\n========== View Service History ==========\n"
        )

        view_service_history()

    elif option == "9":

        logger.info(
            "View Reports Selected"
        )

        print(
            "\n========== View Reports ==========\n"
        )

        view_reports()

    elif option == "10":

        logger.info(
            "AI Assistant Selected"
        )

        print(
            "\n========== AI ASSISTANT ==========\n"
        )

        ai_assistant()

    elif option == "11":

        logger.info(
            "Give Feedback Selected"
        )

        print(
            "\n========== GIVE FEEDBACK ==========\n"
        )

        add_feedback()

    elif option == "12":

        logger.info(
            "View Feedback Selected"
        )

        print(
            "\n========== VIEW FEEDBACK ==========\n"
        )

        view_feedback()

    elif option == "13":

        logger.info(
            "Manage Technician Availability Selected"
        )

        print(
            "\n========== MANAGE TECHNICIAN AVAILABILITY ==========\n"
        )

        manage_technician_availability()

    elif option == "14":

        logger.info(
            "Help / Contact Us Selected"
        )

        print(
            "\n========== HELP / CONTACT US ==========\n"
        )

        help_contact()

    elif option == "0":

        logger.info(
            "Exiting Application"
        )

        print(
            "\nThank You For Using Smart Service Dispatch System."
        )

        break

    else:

        print(
            "\nInvalid Choice! "
            "Please Enter a Valid Option."
        )