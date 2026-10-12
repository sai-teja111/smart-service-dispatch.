from models.person import Person


class Customer(Person):

    def __init__(self,
                 customer_id,
                 customer_name,
                 phone,
                 city,
                 area,
                 pincode):

        super().__init__(customer_name, phone)

        self.customer_id = customer_id
        self.city = city
        self.area = area
        self.pincode = pincode

    def display_customer(self):

        print("\n========== CUSTOMER DETAILS ==========")
        print(f"Customer ID : {self.customer_id}")
        print(f"Name     : {self.name}")
        print(f"Phone    : {self.phone}")
        print(f"City     : {self.city}")
        print(f"Area     : {self.area}")
        print(f"Pincode  : {self.pincode}")