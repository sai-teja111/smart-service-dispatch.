from Orm.database import get_session_context_context
from Orm.customer import Customer


# ============================================================
# INSERT CUSTOMER USING SQLMODEL
# ============================================================

def insert_customer():

    with get_session_context() as session:

        customer = Customer(
            customer_name="ORM Test Customer",
            phone="9999999999",
            city="Hyderabad",
            area="Madhapur",
            pincode="500081"
        )

        session.add(customer)

        session.commit()

        session.refresh(customer)

        print("\nCustomer inserted successfully!")
        print("Customer ID:", customer.customer_id)


# ============================================================
# RUN
# ============================================================

insert_customer()