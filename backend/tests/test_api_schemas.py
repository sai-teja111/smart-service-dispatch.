import pytest

from  datetime import datetime
from  decimal import Decimal
from  uuid import UUID, uuid4

from  pydantic import ValidationError

from Api.schemas import (
    CustomerRegister,
    CustomerRegisterResponse,
    TechnicianRegister,
    TechnicianRegisterResponse,
    LoginRequest,
    TokenResponse,
    AssignedTechnicianResponse,
    TechnicianCustomerResponse,
    TechnicianServiceRequestResponse,
    TechnicianServiceRequestListResponse,
    ServiceDetectionResponse,
    ServiceRequestCreateResponse,
    CustomerServiceRequestResponse,
    CustomerServiceRequestListResponse,
    ServiceHistoryRecordResponse,
    ServiceRequestHistoryResponse,
    TechnicianStatusResponse,
    TechnicianStatusUpdateResponse,
    FeedbackTechnicianResponse,
    FeedbackCreateResponse,
    FeedbackDetailsResponse,
    FeedbackViewResponse,
    TechnicianAvailabilityUpdateResponse,
    TechnicianAvailabilityResponse,
    CustomerTechnicianSummaryResponse,
    ServiceRequestStatusResponse,
    ServicePerformanceResponse,
    TechnicianPerformanceResponse,
    FeedbackSummaryResponse,
    TechnicianWorkloadResponse,
    ReportsResponse,
    AIResponse,
)


# ============================================================
# COMMON TEST DATA
# ============================================================

CUSTOMER_UUID = uuid4()
TECHNICIAN_UUID = uuid4()
REQUEST_UUID = uuid4()
FEEDBACK_UUID = uuid4()

REQUEST_DATE = datetime.now()


def valid_customer_data():
    return {
        "customer_name": "John Doe",
        "phone": "9876543210",
        "password": "Password1!",
        "city": "Hyderabad",
        "area": "Gachibowli",
        "pincode": "500032",
    }


def valid_technician_data():
    return {
        "technician_name": "John Technician",
        "phone": "9876543211",
        "password": "Password1!",
        "city": "Hyderabad",
        "area": "Gachibowli",
        "pincode": "500032",
    }


# ============================================================
# CUSTOMER NAME VALIDATION
# ============================================================

def test_customer_name_valid_and_formatted():

    data = valid_customer_data()

    data["customer_name"] = "  john doe  "

    customer = CustomerRegister(**data)

    assert customer.customer_name == "John Doe"


def test_customer_name_invalid():

    data = valid_customer_data()

    data["customer_name"] = "John123"

    with pytest.raises(
        ValidationError,
        match="Customer name must contain only letters."
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER PHONE VALIDATION
# ============================================================

def test_customer_phone_valid():

    customer = CustomerRegister(
        **valid_customer_data()
    )

    assert customer.phone == "9876543210"


@pytest.mark.parametrize(
    "phone",
    [
        "abcdefghij",
        "123456789",
        "12345678901",
    ]
)
def test_customer_phone_invalid_format(phone):

    data = valid_customer_data()

    data["phone"] = phone

    with pytest.raises(
        ValidationError,
        match="Phone number must contain exactly 10 digits."
    ):
        CustomerRegister(**data)


def test_customer_phone_invalid_start():

    data = valid_customer_data()

    data["phone"] = "5123456789"

    with pytest.raises(
        ValidationError,
        match="Phone number must start with 6, 7, 8 or 9."
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER PASSWORD VALIDATION
# ============================================================

def test_customer_password_valid():

    customer = CustomerRegister(
        **valid_customer_data()
    )

    assert customer.password == "Password1!"


@pytest.mark.parametrize(
    "password, message",
    [
        (
            " Password1!",
            "Password must not contain leading or trailing spaces."
        ),
        (
            "Password1! ",
            "Password must not contain leading or trailing spaces."
        ),
        (
            "password1!",
            "Password must contain at least one uppercase letter."
        ),
        (
            "PASSWORD1!",
            "Password must contain at least one lowercase letter."
        ),
        (
            "Password!!",
            "Password must contain at least one digit."
        ),
        (
            "Password1",
            "Password must contain at least one special character."
        ),
    ]
)
def test_customer_password_invalid(password, message):

    data = valid_customer_data()

    data["password"] = password

    with pytest.raises(
        ValidationError,
        match=message
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER CITY VALIDATION
# ============================================================

def test_customer_city_valid_and_formatted():

    data = valid_customer_data()

    data["city"] = "  HYDERABAD  "

    customer = CustomerRegister(**data)

    assert customer.city == "Hyderabad"


def test_customer_city_invalid():

    data = valid_customer_data()

    data["city"] = "Mumbai"

    with pytest.raises(
        ValidationError,
        match="Currently, service is available only in Hyderabad."
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER AREA VALIDATION
# ============================================================

def test_customer_area_valid_and_formatted():

    data = valid_customer_data()

    data["area"] = "  hiTech city  "

    customer = CustomerRegister(**data)

    assert customer.area == "Hitech City"


def test_customer_area_invalid():

    data = valid_customer_data()

    data["area"] = "Hitech123"

    with pytest.raises(
        ValidationError,
        match="Area must contain only letters."
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER PINCODE VALIDATION
# ============================================================

def test_customer_pincode_valid():

    customer = CustomerRegister(
        **valid_customer_data()
    )

    assert customer.pincode == "500032"


@pytest.mark.parametrize(
    "pincode",
    [
        "abcdef",
        "12345",
        "1234567",
    ]
)
def test_customer_pincode_invalid(pincode):

    data = valid_customer_data()

    data["pincode"] = pincode

    with pytest.raises(
        ValidationError,
        match="Pincode must contain exactly 6 digits."
    ):
        CustomerRegister(**data)


# ============================================================
# CUSTOMER REGISTRATION RESPONSE
# ============================================================

def test_customer_register_response():

    response = CustomerRegisterResponse(
        message="Customer registered successfully.",
        customer_uuid=CUSTOMER_UUID
    )

    assert response.message == "Customer registered successfully."
    assert response.customer_uuid == CUSTOMER_UUID


# ============================================================
# TECHNICIAN NAME VALIDATION
# ============================================================

def test_technician_name_valid_and_formatted():

    data = valid_technician_data()

    data["technician_name"] = "  john technician  "

    technician = TechnicianRegister(**data)

    assert technician.technician_name == "John Technician"


def test_technician_name_invalid():

    data = valid_technician_data()

    data["technician_name"] = "John123"

    with pytest.raises(
        ValidationError,
        match="Technician name must contain only letters."
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN PHONE VALIDATION
# ============================================================

def test_technician_phone_valid():

    technician = TechnicianRegister(
        **valid_technician_data()
    )

    assert technician.phone == "9876543211"


@pytest.mark.parametrize(
    "phone",
    [
        "abcdefghij",
        "123456789",
        "12345678901",
    ]
)
def test_technician_phone_invalid_format(phone):

    data = valid_technician_data()

    data["phone"] = phone

    with pytest.raises(
        ValidationError,
        match="Phone number must contain exactly 10 digits."
    ):
        TechnicianRegister(**data)


def test_technician_phone_invalid_start():

    data = valid_technician_data()

    data["phone"] = "5123456789"

    with pytest.raises(
        ValidationError,
        match="Phone number must start with 6, 7, 8 or 9."
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN PASSWORD VALIDATION
# ============================================================

def test_technician_password_valid():

    technician = TechnicianRegister(
        **valid_technician_data()
    )

    assert technician.password == "Password1!"


@pytest.mark.parametrize(
    "password, message",
    [
        (
            " Password1!",
            "Password must not contain leading or trailing spaces."
        ),
        (
            "Password1! ",
            "Password must not contain leading or trailing spaces."
        ),
        (
            "password1!",
            "Password must contain at least one uppercase letter."
        ),
        (
            "PASSWORD1!",
            "Password must contain at least one lowercase letter."
        ),
        (
            "Password!!",
            "Password must contain at least one digit."
        ),
        (
            "Password1",
            "Password must contain at least one special character."
        ),
    ]
)
def test_technician_password_invalid(password, message):

    data = valid_technician_data()

    data["password"] = password

    with pytest.raises(
        ValidationError,
        match=message
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN CITY VALIDATION
# ============================================================

def test_technician_city_valid_and_formatted():

    data = valid_technician_data()

    data["city"] = "  HYDERABAD  "

    technician = TechnicianRegister(**data)

    assert technician.city == "Hyderabad"


def test_technician_city_invalid():

    data = valid_technician_data()

    data["city"] = "Mumbai"

    with pytest.raises(
        ValidationError,
        match="Currently, service is available only in Hyderabad."
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN AREA VALIDATION
# ============================================================

def test_technician_area_valid_and_formatted():

    data = valid_technician_data()

    data["area"] = "  hiTech city  "

    technician = TechnicianRegister(**data)

    assert technician.area == "Hitech City"


def test_technician_area_invalid():

    data = valid_technician_data()

    data["area"] = "Hitech123"

    with pytest.raises(
        ValidationError,
        match="Area must contain only letters."
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN PINCODE VALIDATION
# ============================================================

def test_technician_pincode_valid():

    technician = TechnicianRegister(
        **valid_technician_data()
    )

    assert technician.pincode == "500032"


@pytest.mark.parametrize(
    "pincode",
    [
        "abcdef",
        "12345",
        "1234567",
    ]
)
def test_technician_pincode_invalid(pincode):

    data = valid_technician_data()

    data["pincode"] = pincode

    with pytest.raises(
        ValidationError,
        match="Pincode must contain exactly 6 digits."
    ):
        TechnicianRegister(**data)


# ============================================================
# TECHNICIAN REGISTRATION RESPONSE
# ============================================================

def test_technician_register_response():

    response = TechnicianRegisterResponse(
        message="Technician registered successfully.",
        technician_uuid=TECHNICIAN_UUID
    )

    assert response.message == "Technician registered successfully."
    assert response.technician_uuid == TECHNICIAN_UUID


# ============================================================
# LOGIN REQUEST
# ============================================================

def test_login_request_valid():

    login = LoginRequest(
        phone="9876543210",
        password="Password1!"
    )

    assert login.phone == "9876543210"
    assert login.password == "Password1!"


@pytest.mark.parametrize(
    "phone",
    [
        "abcdefghij",
        "123456789",
        "12345678901",
    ]
)
def test_login_phone_invalid(phone):

    with pytest.raises(
        ValidationError,
        match="Phone number must contain exactly 10 digits."
    ):
        LoginRequest(
            phone=phone,
            password="Password1!"
        )


# ============================================================
# TOKEN RESPONSE
# ============================================================

def test_token_response():

    response = TokenResponse(
        access_token="test-token",
        token_type="bearer"
    )

    assert response.access_token == "test-token"
    assert response.token_type == "bearer"


# ============================================================
# ASSIGNED TECHNICIAN RESPONSE
# ============================================================

def test_assigned_technician_response():

    response = AssignedTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician"
    )

    assert response.technician_uuid == TECHNICIAN_UUID
    assert response.technician_name == "John Technician"


# ============================================================
# TECHNICIAN CUSTOMER RESPONSE
# ============================================================

def test_technician_customer_response():

    response = TechnicianCustomerResponse(
        customer_uuid=CUSTOMER_UUID,
        customer_name="John Doe",
        phone="9876543210",
        city="Hyderabad",
        area="Gachibowli",
        pincode="500032"
    )

    assert response.customer_uuid == CUSTOMER_UUID
    assert response.customer_name == "John Doe"
    assert response.phone == "9876543210"


# ============================================================
# TECHNICIAN SERVICE REQUEST RESPONSE
# ============================================================

def test_technician_service_request_response():

    customer = TechnicianCustomerResponse(
        customer_uuid=CUSTOMER_UUID,
        customer_name="John Doe",
        phone="9876543210",
        city="Hyderabad",
        area="Gachibowli",
        pincode="500032"
    )

    response = TechnicianServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="AC Repair",
        problem_description="AC is not cooling",
        priority="HIGH",
        status="OPEN",
        request_date=REQUEST_DATE,
        customer=customer
    )

    assert response.request_uuid == REQUEST_UUID
    assert response.service == "AC Repair"
    assert response.customer.customer_uuid == CUSTOMER_UUID


def test_technician_service_request_response_optional_priority():

    customer = TechnicianCustomerResponse(
        customer_uuid=CUSTOMER_UUID,
        customer_name="John Doe",
        phone="9876543210",
        city="Hyderabad",
        area="Gachibowli",
        pincode="500032"
    )

    response = TechnicianServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="Plumbing",
        problem_description="Water leakage",
        priority=None,
        status="OPEN",
        request_date=REQUEST_DATE,
        customer=customer
    )

    assert response.priority is None


# ============================================================
# TECHNICIAN SERVICE REQUEST LIST
# ============================================================

def test_technician_service_request_list_response():

    customer = TechnicianCustomerResponse(
        customer_uuid=CUSTOMER_UUID,
        customer_name="John Doe",
        phone="9876543210",
        city="Hyderabad",
        area="Gachibowli",
        pincode="500032"
    )

    request = TechnicianServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="AC Repair",
        problem_description="AC problem",
        priority="HIGH",
        status="OPEN",
        request_date=REQUEST_DATE,
        customer=customer
    )

    response = TechnicianServiceRequestListResponse(
        count=1,
        service_requests=[request]
    )

    assert response.count == 1
    assert len(response.service_requests) == 1


# ============================================================
# SERVICE DETECTION RESPONSE
# ============================================================

def test_service_detection_response():

    response = ServiceDetectionResponse(
        match_type="Semantic Match",
        distance=0.25
    )

    assert response.match_type == "Semantic Match"
    assert response.distance == 0.25


def test_service_detection_response_optional_values():

    response = ServiceDetectionResponse(
        match_type=None,
        distance=None
    )

    assert response.match_type is None
    assert response.distance is None


# ============================================================
# SERVICE REQUEST CREATE RESPONSE
# ============================================================

def test_service_request_create_response_complete():

    technician = AssignedTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician"
    )

    detection = ServiceDetectionResponse(
        match_type="Keyword Match",
        distance=0.1
    )

    response = ServiceRequestCreateResponse(
        message="Service request created successfully.",
        request_uuid=REQUEST_UUID,
        service="AC Repair",
        priority="HIGH",
        status="OPEN",
        service_detection=detection,
        technician=technician
    )

    assert response.request_uuid == REQUEST_UUID
    assert response.service_detection.match_type == "Keyword Match"
    assert response.technician.technician_uuid == TECHNICIAN_UUID


def test_service_request_create_response_optional_values():

    response = ServiceRequestCreateResponse(
        message="Created",
        request_uuid=REQUEST_UUID,
        service="Plumbing",
        priority="MEDIUM",
        status="OPEN"
    )

    assert response.service_detection is None
    assert response.technician is None


# ============================================================
# CUSTOMER SERVICE REQUEST RESPONSE
# ============================================================

def test_customer_service_request_response_complete():

    technician = AssignedTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician"
    )

    response = CustomerServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="AC Repair",
        problem_description="Not cooling",
        priority="HIGH",
        status="OPEN",
        request_date=REQUEST_DATE,
        technician=technician
    )

    assert response.request_uuid == REQUEST_UUID
    assert response.technician.technician_uuid == TECHNICIAN_UUID


def test_customer_service_request_response_without_technician():

    response = CustomerServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="Plumbing",
        problem_description="Leakage",
        priority=None,
        status="OPEN",
        request_date=REQUEST_DATE
    )

    assert response.priority is None
    assert response.technician is None


# ============================================================
# CUSTOMER SERVICE REQUEST LIST
# ============================================================

def test_customer_service_request_list_response():

    request = CustomerServiceRequestResponse(
        request_uuid=REQUEST_UUID,
        service="AC Repair",
        problem_description="Not cooling",
        priority="HIGH",
        status="OPEN",
        request_date=REQUEST_DATE
    )

    response = CustomerServiceRequestListResponse(
        count=1,
        service_requests=[request]
    )

    assert response.count == 1
    assert len(response.service_requests) == 1


# ============================================================
# SERVICE HISTORY
# ============================================================

def test_service_history_record_response():

    response = ServiceHistoryRecordResponse(
        old_status="OPEN",
        new_status="IN PROGRESS",
        remarks="Technician assigned",
        updated_time=REQUEST_DATE
    )

    assert response.old_status == "OPEN"
    assert response.new_status == "IN PROGRESS"
    assert response.remarks == "Technician assigned"


def test_service_history_record_response_optional_values():

    response = ServiceHistoryRecordResponse(
        old_status=None,
        new_status=None,
        remarks=None,
        updated_time=REQUEST_DATE
    )

    assert response.old_status is None
    assert response.new_status is None
    assert response.remarks is None


def test_service_request_history_response():

    record = ServiceHistoryRecordResponse(
        old_status="OPEN",
        new_status="COMPLETED",
        remarks="Service completed",
        updated_time=REQUEST_DATE
    )

    response = ServiceRequestHistoryResponse(
        request_uuid=REQUEST_UUID,
        count=1,
        history=[record]
    )

    assert response.request_uuid == REQUEST_UUID
    assert response.count == 1
    assert len(response.history) == 1


# ============================================================
# TECHNICIAN STATUS
# ============================================================

def test_technician_status_response():

    response = TechnicianStatusResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        previous_workload=2,
        new_workload=3,
        availability="Available",
        availability_changed=True
    )

    assert response.previous_workload == 2
    assert response.new_workload == 3
    assert response.availability_changed is True


def test_technician_status_update_response():

    technician = TechnicianStatusResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        previous_workload=2,
        new_workload=3,
        availability="Available",
        availability_changed=False
    )

    response = TechnicianStatusUpdateResponse(
        message="Status updated successfully.",
        request_uuid=REQUEST_UUID,
        old_status="OPEN",
        new_status="IN PROGRESS",
        remarks="Technician started work",
        technician=technician
    )

    assert response.message == "Status updated successfully."
    assert response.technician.new_workload == 3


def test_technician_status_update_response_without_remarks():

    technician = TechnicianStatusResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        previous_workload=3,
        new_workload=2,
        availability="Available",
        availability_changed=True
    )

    response = TechnicianStatusUpdateResponse(
        message="Completed",
        request_uuid=REQUEST_UUID,
        old_status="IN PROGRESS",
        new_status="COMPLETED",
        remarks=None,
        technician=technician
    )

    assert response.remarks is None


# ============================================================
# FEEDBACK
# ============================================================

def test_feedback_technician_response():

    response = FeedbackTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        rating=Decimal("4.5")
    )

    assert response.rating == Decimal("4.5")


def test_feedback_technician_response_without_rating():

    response = FeedbackTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician"
    )

    assert response.rating is None


def test_feedback_create_response():

    technician = FeedbackTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        rating=Decimal("4.5")
    )

    response = FeedbackCreateResponse(
        message="Feedback submitted successfully.",
        feedback_uuid=FEEDBACK_UUID,
        request_uuid=REQUEST_UUID,
        rating=Decimal("5.0"),
        comments="Good service",
        technician=technician
    )

    assert response.feedback_uuid == FEEDBACK_UUID
    assert response.rating == Decimal("5.0")
    assert response.technician.rating == Decimal("4.5")


def test_feedback_create_response_optional_values():

    technician = FeedbackTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician"
    )

    response = FeedbackCreateResponse(
        message="Submitted",
        feedback_uuid=FEEDBACK_UUID,
        request_uuid=REQUEST_UUID,
        technician=technician
    )

    assert response.rating is None
    assert response.comments is None


def test_feedback_details_response():

    response = FeedbackDetailsResponse(
        feedback_uuid=FEEDBACK_UUID,
        rating=Decimal("4.5"),
        comments="Excellent",
        feedback_date=REQUEST_DATE
    )

    assert response.feedback_uuid == FEEDBACK_UUID
    assert response.rating == Decimal("4.5")


def test_feedback_details_response_optional_values():

    response = FeedbackDetailsResponse(
        feedback_uuid=FEEDBACK_UUID,
        rating=None,
        comments=None,
        feedback_date=REQUEST_DATE
    )

    assert response.rating is None
    assert response.comments is None


def test_feedback_view_response_complete():

    details = FeedbackDetailsResponse(
        feedback_uuid=FEEDBACK_UUID,
        rating=Decimal("4.0"),
        comments="Good",
        feedback_date=REQUEST_DATE
    )

    technician = FeedbackTechnicianResponse(
        technician_uuid=TECHNICIAN_UUID,
        technician_name="John Technician",
        rating=Decimal("4.2")
    )

    response = FeedbackViewResponse(
        request_uuid=REQUEST_UUID,
        message="Feedback found.",
        feedback=details,
        technician=technician
    )

    assert response.feedback.feedback_uuid == FEEDBACK_UUID
    assert response.technician.technician_uuid == TECHNICIAN_UUID


def test_feedback_view_response_without_feedback():

    response = FeedbackViewResponse(
        request_uuid=REQUEST_UUID,
        message="No feedback found.",
        feedback=None,
        technician=None
    )

    assert response.feedback is None
    assert response.technician is None


# ============================================================
# AVAILABILITY
# ============================================================

def test_technician_availability_update_response():

    response = TechnicianAvailabilityUpdateResponse(
        message="Availability updated successfully.",
        technician_uuid=TECHNICIAN_UUID,
        old_availability="Busy",
        new_availability="Available"
    )

    assert response.old_availability == "Busy"
    assert response.new_availability == "Available"


def test_technician_availability_response():

    response = TechnicianAvailabilityResponse(
        technician_uuid=TECHNICIAN_UUID,
        availability="Available"
    )

    assert response.technician_uuid == TECHNICIAN_UUID
    assert response.availability == "Available"


# ============================================================
# REPORTS
# ============================================================

def test_customer_technician_summary_response():

    response = CustomerTechnicianSummaryResponse(
        total_customers=10,
        total_technicians=5,
        total_services=20,
        total_service_requests=15
    )

    assert response.total_customers == 10
    assert response.total_technicians == 5
    assert response.total_services == 20
    assert response.total_service_requests == 15


def test_service_request_status_response():

    response = ServiceRequestStatusResponse(
        open_requests=2,
        pending_requests=3,
        in_progress_requests=4,
        completed_requests=6
    )

    assert response.open_requests == 2
    assert response.pending_requests == 3
    assert response.in_progress_requests == 4
    assert response.completed_requests == 6


def test_service_performance_response_complete():

    response = ServicePerformanceResponse(
        most_requested_service="AC Repair",
        total_requests_for_service=10
    )

    assert response.most_requested_service == "AC Repair"
    assert response.total_requests_for_service == 10


def test_service_performance_response_without_service():

    response = ServicePerformanceResponse(
        total_requests_for_service=0
    )

    assert response.most_requested_service is None


def test_technician_performance_response_complete():

    response = TechnicianPerformanceResponse(
        highest_rated_technician="John Technician",
        highest_rating=Decimal("4.8"),
        average_technician_rating=4.3
    )

    assert response.highest_rated_technician == "John Technician"
    assert response.highest_rating == Decimal("4.8")
    assert response.average_technician_rating == 4.3


def test_technician_performance_response_without_highest_rating():

    response = TechnicianPerformanceResponse(
        highest_rated_technician=None,
        highest_rating=None,
        average_technician_rating=0
    )

    assert response.highest_rated_technician is None
    assert response.highest_rating is None


def test_feedback_summary_response():

    response = FeedbackSummaryResponse(
        total_feedback=10,
        average_customer_rating=4.5
    )

    assert response.total_feedback == 10
    assert response.average_customer_rating == 4.5


def test_technician_workload_response():

    response = TechnicianWorkloadResponse(
        technician_id=1,
        technician_name="John Technician",
        workload=3,
        rating=Decimal("4.5")
    )

    assert response.technician_id == 1
    assert response.workload == 3
    assert response.rating == Decimal("4.5")


def test_technician_workload_response_without_rating():

    response = TechnicianWorkloadResponse(
        technician_id=2,
        technician_name="David Technician",
        workload=0
    )

    assert response.rating is None


def test_reports_response():

    response = ReportsResponse(
        customer_technician_summary=CustomerTechnicianSummaryResponse(
            total_customers=10,
            total_technicians=5,
            total_services=20,
            total_service_requests=15
        ),
        service_request_status=ServiceRequestStatusResponse(
            open_requests=2,
            pending_requests=3,
            in_progress_requests=4,
            completed_requests=6
        ),
        service_performance=ServicePerformanceResponse(
            most_requested_service="AC Repair",
            total_requests_for_service=10
        ),
        technician_performance=TechnicianPerformanceResponse(
            highest_rated_technician="John Technician",
            highest_rating=Decimal("4.8"),
            average_technician_rating=4.4
        ),
        feedback_summary=FeedbackSummaryResponse(
            total_feedback=10,
            average_customer_rating=4.5
        ),
        technician_workload=[
            TechnicianWorkloadResponse(
                technician_id=1,
                technician_name="John Technician",
                workload=3,
                rating=Decimal("4.8")
            )
        ]
    )

    assert (
        response.customer_technician_summary.total_customers
        == 10
    )

    assert (
        response.service_request_status.completed_requests
        == 6
    )

    assert (
        response.service_performance.most_requested_service
        == "AC Repair"
    )

    assert (
        response.technician_performance.highest_rating
        == Decimal("4.8")
    )

    assert (
        response.feedback_summary.average_customer_rating
        == 4.5
    )

    assert len(response.technician_workload) == 1


# ============================================================
# AI RESPONSE
# ============================================================

def test_ai_response():

    response = AIResponse(
        question="Show all customers",
        sql="SELECT * from  customers;",
        result_count=2,
        results=[
            {
                "customer_id": 1,
                "customer_name": "John"
            },
            {
                "customer_id": 2,
                "customer_name": "David"
            }
        ]
    )

    assert response.question == "Show all customers"
    assert response.sql == "SELECT * from  customers;"
    assert response.result_count == 2
    assert len(response.results) == 2


def test_ai_response_empty_results():

    response = AIResponse(
        question="Show customers",
        sql="SELECT * from  customers;",
        result_count=0,
        results=[]
    )

    assert response.result_count == 0
    assert response.results == []