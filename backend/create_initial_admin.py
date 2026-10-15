from getpass import getpass

from fastapi import HTTPException
from pydantic import ValidationError

# Import the Admin model before creating tables.
from Orm.admin import Admin
from Orm.database import create_db_and_tables

from Api.admin_schemas import AdminProvision
from modules.admin_service import provision_initial_admin


def main():
    print("\n=== Smart Service Dispatch System ===")
    print("Initial Admin Setup\n")

    admin_name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip()

    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    if password != confirm_password:
        print("\nError: Passwords do not match.")
        return

    try:
        # Validate all admin registration inputs.
        admin_data = AdminProvision(
            admin_name=admin_name,
            email=email,
            password=password,
        )

        # Register the model and create missing database tables.
        create_db_and_tables()

        # Create the initial administrator.
        admin = provision_initial_admin(admin_data)

        print("\nAdmin account created successfully.")
        print(f"Admin UUID: {admin['admin_uuid']}")
        print(f"Admin name: {admin['admin_name']}")
        print(f"Admin email: {admin['email']}")
        print(f"Active: {admin['is_active']}")

        print("\nYou can now log in through POST /admin/login.")

    except ValidationError as error:
        print("\nInvalid input:")

        for item in error.errors():
            field = ".".join(
                str(part) for part in item["loc"]
            )
            print(f"- {field}: {item['msg']}")

    except HTTPException as error:
        print(f"\nAdmin setup failed: {error.detail}")

    except Exception:
        import traceback

        print("\nAdmin setup failed. Actual error:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
