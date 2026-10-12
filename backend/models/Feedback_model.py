class Feedback:

    def __init__(
        self,
        request_id,
        customer_id,
        technician_id,
        rating,
        comments,
        feedback_date=None,
        feedback_id=None
    ):

        self.feedback_id = feedback_id
        self.request_id = request_id
        self.customer_id = customer_id
        self.technician_id = technician_id
        self.rating = rating
        self.comments = comments
        self.feedback_date = feedback_date

    def display_feedback(self):

        print("\n========== FEEDBACK DETAILS ==========")

        print(f"Feedback ID    : {self.feedback_id}")
        print(f"Request ID     : {self.request_id}")
        print(f"Customer ID    : {self.customer_id}")
        print(f"Technician ID  : {self.technician_id}")
        print(f"Rating         : {self.rating}/5")
        print(f"Comments       : {self.comments}")
        print(f"Feedback Date  : {self.feedback_date}")

        print("--------------------------------------")