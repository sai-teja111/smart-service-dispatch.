from Orm.database import get_session_context


try:

    with get_session_context() as session:

        print("\nSQLModel database connection successful!")

except Exception as error:

    print("\nSQLModel database connection failed.")
    print(error)