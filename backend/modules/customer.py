from  getpass import getpass

from  sqlmodel import select

from Orm.database import get_session_context
from Orm.customer import Customer as CustomerORM

from models.customer_model import Customer

from Api.security import hash_password


def register_customer():

    try:

        customer_name = input(
            "Enter Customer Name : "
        )

        while True:

            phone = input(
                "Enter Phone Number : "
            )

            if (
                phone.isdigit()
                and len(phone) == 10
                and phone[0] in "6789"
            ):
                break

            print(
                "Invalid Phone Number! "
                "Enter a valid 10-digit mobile number."
            )

        while True:

            password = getpass(
                "Enter Password : "
            )

            if password != password.strip():

                print(
                    "Password must not contain "
                    "leading or trailing spaces."
                )

                continue

            if len(password) < 8:

                print(
                    "Password must contain at least "
                    "8 characters."
                )

                continue

            if not any(
                char.isupper()
                for char in password
            ):

                print(
                    "Password must contain at least "
                    "one uppercase letter."
                )

                continue

            if not any(
                char.islower()
                for char in password
            ):

                print(
                    "Password must contain at least "
                    "one lowercase letter."
                )

                continue

            if not any(
                char.isdigit()
                for char in password
            ):

                print(
                    "Password must contain at least "
                    "one digit."
                )

                continue

            if not any(
                not char.isalnum()
                and not char.isspace()
                for char in password
            ):

                print(
                    "Password must contain at least "
                    "one special character."
                )

                continue

            break

        city = input(
            "Enter City : "
        )

        area = input(
            "Enter Area : "
        )

        pincode = input(
            "Enter Pincode : "
        )

        customer = Customer(
            None,
            customer_name,
            phone,
            city,
            area,
            pincode
        )

        with get_session_context() as session:

            statement = select(
                CustomerORM
            ).where(
                CustomerORM.phone == customer.phone
            )

            existing_customer = (
                session.exec(statement).first()
            )

            if existing_customer:

                print(
                    "\nCustomer already exists "
                    "with this phone number."
                )

                return

            password_hash = hash_password(
                password
            )

            customer_orm = CustomerORM(
                customer_name=customer.name,
                phone=customer.phone,
                password_hash=password_hash,
                city=customer.city,
                area=customer.area,
                pincode=customer.pincode
            )

            session.add(customer_orm)

            session.commit()

            session.refresh(customer_orm)

            print(
                "\nCustomer Registered Successfully."
            )

            print(
                f"Customer ID   : "
                f"{customer_orm.customer_id}"
            )

            print(
                f"Customer UUID : "
                f"{customer_orm.customer_uuid}"
            )

    except Exception as err:

        print(
            "\nError :",
            err
        )


def view_customers():

    try:

        with get_session_context() as session:

            statement = (
                select(CustomerORM)
                .order_by(
                    CustomerORM.customer_id
                )
            )

            customers = (
                session.exec(statement).all()
            )

            if not customers:

                print(
                    "\nNo Customers Found."
                )

                return

            for customer_orm in customers:

                print(
                    f"\nCustomer ID   : "
                    f"{customer_orm.customer_id}"
                )

                print(
                    f"Customer UUID : "
                    f"{customer_orm.customer_uuid}"
                )

                customer = Customer(
                    customer_orm.customer_id,
                    customer_orm.customer_name,
                    customer_orm.phone,
                    customer_orm.city,
                    customer_orm.area,
                    customer_orm.pincode
                )

                customer.display_customer()

                print(
                    "-------------------------------------"
                )

    except Exception as err:

        print(
            "\nError :",
            err
        )