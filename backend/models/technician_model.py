from models.person import Person


class Technician(Person):

    def __init__(self,
                 technician_name,
                 phone,
                 city,
                 area,
                 pincode,
                 availability="Available",
                 workload=0,
                 rating=0):

        super().__init__(technician_name, phone)

        self.city = city
        self.area = area
        self.pincode = pincode
        self.availability = availability
        self.workload = workload
        self.rating = rating

    def display_technician(self):

        print("\n========== TECHNICIAN DETAILS ==========")
        print(f"Name         : {self.name}")
        print(f"Phone        : {self.phone}")
        print(f"City         : {self.city}")
        print(f"Area         : {self.area}")
        print(f"Pincode      : {self.pincode}")
        print(f"Availability : {self.availability}")
        print(f"Workload     : {self.workload}")
        print(f"Rating       : {self.rating}")