
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# ============================================================
# CUSTOMER REGISTRATION
# ============================================================

class CustomerRegister(BaseModel):

    customer_name: str = Field(
        min_length=1,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    password: str = Field(
        min_length=8,
        max_length=72
    )

    city: str = Field(
        max_length=50
    )

    area: str = Field(
        max_length=100
    )

    pincode: str = Field(
        min_length=6,
        max_length=6
    )

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Customer name must contain only letters."
            )

        return value.title()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        if value[0] not in "6789":
            raise ValueError(
                "Phone number must start with 6, 7, 8 or 9."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if value != value.strip():
            raise ValueError(
                "Password must not contain leading or trailing spaces."
            )

        if not any(char.isupper() for char in value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.islower() for char in value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not any(char.isdigit() for char in value):
            raise ValueError(
                "Password must contain at least one digit."
            )

        if not any(
            not char.isalnum() and not char.isspace()
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one special character."
            )

        return value

    @field_validator("city")
    @classmethod
    def validate_city(cls, value):

        value = value.strip().lower()

        if value != "hyderabad":
            raise ValueError(
                "Currently, service is available only in Hyderabad."
            )

        return "Hyderabad"

    @field_validator("area")
    @classmethod
    def validate_area(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Area must contain only letters."
            )

        return value.title()

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 6:
            raise ValueError(
                "Pincode must contain exactly 6 digits."
            )

        return value


# ============================================================
# CUSTOMER REGISTRATION RESPONSE
# ============================================================

class CustomerRegisterResponse(BaseModel):

    message: str
    customer_uuid: UUID


# ============================================================
# TECHNICIAN SKILL INPUT
# ============================================================

class TechnicianSkillInput(BaseModel):

    skill_id: int = Field(gt=0)

    experience_years: int = Field(
        ge=0,
        le=50
    )

    expertise_level: str = Field(
        min_length=1,
        max_length=20
    )

    @field_validator("expertise_level")
    @classmethod
    def validate_expertise_level(cls, value):

        value = value.strip()

        allowed_levels = {
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert"
        }

        if value not in allowed_levels:
            raise ValueError(
                "Expertise level must be Beginner, Intermediate, Advanced, or Expert."
            )

        return value


# ============================================================
# TECHNICIAN REGISTRATION
# ============================================================

class TechnicianRegister(BaseModel):

    technician_name: str = Field(
        min_length=1,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    password: str = Field(
        min_length=8,
        max_length=72
    )

    city: str = Field(max_length=50)
    area: str = Field(max_length=100)

    pincode: str = Field(
        min_length=6,
        max_length=6
    )

    skills: list[TechnicianSkillInput] = Field(
        min_length=1
    )

    @field_validator("technician_name")
    @classmethod
    def validate_technician_name(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Technician name must contain only letters."
            )

        return value.title()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        if value[0] not in "6789":
            raise ValueError(
                "Phone number must start with 6, 7, 8 or 9."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if value != value.strip():
            raise ValueError(
                "Password must not contain leading or trailing spaces."
            )

        if not any(char.isupper() for char in value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not any(char.islower() for char in value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not any(char.isdigit() for char in value):
            raise ValueError(
                "Password must contain at least one digit."
            )

        if not any(
            not char.isalnum() and not char.isspace()
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one special character."
            )

        return value

    @field_validator("city")
    @classmethod
    def validate_city(cls, value):

        value = value.strip().lower()

        if value != "hyderabad":
            raise ValueError(
                "Currently, service is available only in Hyderabad."
            )

        return "Hyderabad"

    @field_validator("area")
    @classmethod
    def validate_area(cls, value):

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Area must contain only letters."
            )

        return value.title()

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 6:
            raise ValueError(
                "Pincode must contain exactly 6 digits."
            )

        return value


# ============================================================
# TECHNICIAN REGISTRATION RESPONSE
# ============================================================

class TechnicianRegisterResponse(BaseModel):

    message: str
    technician_uuid: UUID


# ============================================================
# LOGIN REQUEST
# ============================================================

class LoginRequest(BaseModel):

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    password: str = Field(min_length=1)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        value = value.strip()

        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        return value


# ============================================================
# TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):

    access_token: str
    token_type: str
    user_uuid: UUID
    name: str
    role: str
    first_login: bool


# ============================================================
# TECHNICIAN RESPONSE
# ============================================================

class AssignedTechnicianResponse(BaseModel):

    technician_uuid: UUID
    technician_name: str


# ============================================================
# TECHNICIAN SERVICE REQUEST RESPONSE
# ============================================================

class TechnicianCustomerResponse(BaseModel):

    customer_uuid: UUID
    customer_name: str
    phone: str
    city: str
    area: str
    pincode: str


class TechnicianServiceRequestResponse(BaseModel):

    request_uuid: UUID
    service: str
    problem_description: str
    priority: str | None
    status: str
    request_date: datetime
    customer: TechnicianCustomerResponse


class TechnicianServiceRequestListResponse(BaseModel):

    count: int
    service_requests: list[TechnicianServiceRequestResponse]


# ============================================================
# SERVICE DETECTION RESPONSE
# ============================================================

class ServiceDetectionResponse(BaseModel):

    skill_id: int | None = None
    skill_name: str | None = None
    category: str | None = None
    match_type: str | None = None
    distance: float | None = None


# ============================================================
# AVAILABLE SERVICE RESPONSE
# ============================================================

class AvailableServiceResponse(BaseModel):

    skill_id: int
    skill_name: str


# ============================================================
# SERVICE DETECTION STAGE RESPONSE
# ============================================================

class ServiceDetectionStageResponse(BaseModel):

    message: str

    service_detection: ServiceDetectionResponse | None = None

    available_services: list[AvailableServiceResponse] = Field(
        default_factory=list
    )


# ============================================================
# CREATE SERVICE REQUEST RESPONSE
# ============================================================

class ServiceRequestCreateResponse(BaseModel):

    message: str
    request_uuid: UUID
    service: str
    priority: str
    status: str
    service_detection: ServiceDetectionResponse | None = None
    technician: AssignedTechnicianResponse | None = None


# ============================================================
# CUSTOMER SERVICE REQUEST RESPONSE
# ============================================================

class CustomerServiceRequestResponse(BaseModel):

    request_uuid: UUID
    service: str
    problem_description: str
    priority: str | None
    status: str
    request_date: datetime
    technician: AssignedTechnicianResponse | None = None


class CustomerServiceRequestListResponse(BaseModel):

    count: int
    service_requests: list[CustomerServiceRequestResponse]


# ============================================================
# SERVICE HISTORY RESPONSE
# ============================================================

class ServiceHistoryRecordResponse(BaseModel):

    old_status: str | None
    new_status: str | None
    remarks: str | None
    updated_time: datetime


class ServiceRequestHistoryResponse(BaseModel):

    request_uuid: UUID
    count: int
    history: list[ServiceHistoryRecordResponse]


# ============================================================
# SERVICE REQUEST STATUS UPDATE RESPONSE
# ============================================================

class TechnicianStatusResponse(BaseModel):

    technician_uuid: UUID
    technician_name: str
    previous_workload: int
    new_workload: int
    availability: str
    availability_changed: bool


class TechnicianStatusUpdateResponse(BaseModel):

    message: str
    request_uuid: UUID
    old_status: str
    new_status: str
    remarks: str | None
    technician: TechnicianStatusResponse


# ============================================================
# FEEDBACK RESPONSE MODELS
# ============================================================

class FeedbackTechnicianResponse(BaseModel):

    technician_uuid: UUID
    technician_name: str
    rating: Decimal | None = None


class FeedbackCreateResponse(BaseModel):

    message: str
    feedback_uuid: UUID
    request_uuid: UUID
    rating: Decimal | None = None
    comments: str | None = None
    technician: FeedbackTechnicianResponse


class FeedbackDetailsResponse(BaseModel):

    feedback_uuid: UUID
    rating: Decimal | None = None
    comments: str | None = None
    feedback_date: datetime


class FeedbackViewResponse(BaseModel):

    request_uuid: UUID
    message: str | None = None
    feedback: FeedbackDetailsResponse | None = None
    technician: FeedbackTechnicianResponse | None = None


# ============================================================
# TECHNICIAN AVAILABILITY RESPONSE MODELS
# ============================================================

class TechnicianAvailabilityUpdateResponse(BaseModel):

    message: str
    technician_uuid: UUID
    old_availability: str
    new_availability: str


class TechnicianAvailabilityResponse(BaseModel):

    technician_uuid: UUID
    availability: str


# ============================================================
# REPORTS RESPONSE MODELS
# ============================================================

class CustomerTechnicianSummaryResponse(BaseModel):

    total_customers: int
    total_technicians: int
    total_services: int
    total_service_requests: int


class ServiceRequestStatusResponse(BaseModel):

    open_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int


class ServicePerformanceResponse(BaseModel):

    most_requested_service: str | None = None
    total_requests_for_service: int


class TechnicianPerformanceResponse(BaseModel):

    highest_rated_technician: str | None = None
    highest_rating: Decimal | None = None
    average_technician_rating: float


class FeedbackSummaryResponse(BaseModel):

    total_feedback: int
    average_customer_rating: float


class TechnicianWorkloadResponse(BaseModel):

    technician_id: int
    technician_name: str
    workload: int
    rating: Decimal | None = None


class ReportsResponse(BaseModel):

    customer_technician_summary: CustomerTechnicianSummaryResponse
    service_request_status: ServiceRequestStatusResponse
    service_performance: ServicePerformanceResponse
    technician_performance: TechnicianPerformanceResponse
    feedback_summary: FeedbackSummaryResponse
    technician_workload: list[TechnicianWorkloadResponse]


# ============================================================
# CUSTOMER REPORT RESPONSE MODELS
# ============================================================

class CustomerReportRecordResponse(BaseModel):

    request_uuid: UUID
    service: str
    problem_description: str
    priority: str | None = None
    status: str
    request_date: datetime
    technician: AssignedTechnicianResponse | None = None


class CustomerReportsResponse(BaseModel):

    count: int
    reports: list[CustomerReportRecordResponse]


# ============================================================
# AI RESPONSE
# ============================================================

class AIResponse(BaseModel):

    question: str
    sql: str
    result_count: int
    results: list
    answer: str | None = None
