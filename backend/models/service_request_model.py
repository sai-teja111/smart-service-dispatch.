class ServiceRequest:

    def __init__(
        self,
        customer_id,
        skill_id,
        problem_description,
        priority,
        assigned_technician_id=None,
        status="OPEN",
        request_date=None,
        request_id=None
    ):

        self.request_id = request_id
        self.customer_id = customer_id
        self.skill_id = skill_id
        self.problem_description = problem_description
        self.priority = priority
        self.assigned_technician_id = assigned_technician_id
        self.status = status
        self.request_date = request_date

    def display_request(self):

        print("\n========== SERVICE REQUEST DETAILS ==========")
        print(f"Request ID             : {self.request_id}")
        print(f"Customer ID            : {self.customer_id}")
        print(f"Skill ID               : {self.skill_id}")
        print(f"Problem Description    : {self.problem_description}")
        print(f"Priority               : {self.priority}")
        print(f"Assigned Technician ID : {self.assigned_technician_id}")
        print(f"Status                 : {self.status}")
        print(f"Request Date           : {self.request_date}")