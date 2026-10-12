class Person:

    def __init__(self, name, phone):

        self.name = name
        self.phone = phone

    def display_person(self):

        print("\nPerson Details")
        print("----------------------")
        print(f"Name  : {self.name}")
        print(f"Phone : {self.phone}")