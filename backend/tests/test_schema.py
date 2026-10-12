# ============================================================
# TESTS FOR Ai/schema.py
# ============================================================

from Ai.schema import DATABASE_SCHEMA


# ============================================================
# DATABASE SCHEMA
# ============================================================

def test_database_schema_exists():

    assert DATABASE_SCHEMA


def test_database_name():

    assert (
        "DATABASE: Smart Service Dispatch System"
        in DATABASE_SCHEMA
    )


# ============================================================
# TABLES
# ============================================================

def test_customers_table():

    assert "TABLE: customers" in DATABASE_SCHEMA


def test_technicians_table():

    assert "TABLE: technicians" in DATABASE_SCHEMA


def test_skills_table():

    assert "TABLE: skills" in DATABASE_SCHEMA


def test_technician_skills_table():

    assert "TABLE: technician_skills" in DATABASE_SCHEMA


def test_service_requests_table():

    assert "TABLE: service_requests" in DATABASE_SCHEMA


def test_assignments_table():

    assert "TABLE: assignments" in DATABASE_SCHEMA


def test_service_history_table():

    assert "TABLE: service_history" in DATABASE_SCHEMA


def test_feedback_table():

    assert "TABLE: feedback" in DATABASE_SCHEMA


# ============================================================
# CUSTOMER COLUMNS
# ============================================================

def test_customer_columns():

    assert "customer_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "customer_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "customer_name VARCHAR(100)" in DATABASE_SCHEMA
    assert "phone VARCHAR(15)" in DATABASE_SCHEMA
    assert "city VARCHAR(50)" in DATABASE_SCHEMA
    assert "area VARCHAR(100)" in DATABASE_SCHEMA
    assert "pincode VARCHAR(10)" in DATABASE_SCHEMA


# ============================================================
# TECHNICIAN COLUMNS
# ============================================================

def test_technician_columns():

    assert "technician_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "technician_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "technician_name VARCHAR(100)" in DATABASE_SCHEMA
    assert "phone VARCHAR(15)" in DATABASE_SCHEMA
    assert "city VARCHAR(50)" in DATABASE_SCHEMA
    assert "area VARCHAR(100)" in DATABASE_SCHEMA
    assert "pincode VARCHAR(10)" in DATABASE_SCHEMA
    assert "availability VARCHAR(20)" in DATABASE_SCHEMA
    assert "workload INTEGER" in DATABASE_SCHEMA
    assert "rating DECIMAL(2,1)" in DATABASE_SCHEMA


# ============================================================
# SKILL COLUMNS
# ============================================================

def test_skill_columns():

    assert "skill_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "skill_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "skill_name VARCHAR(100)" in DATABASE_SCHEMA
    assert "category VARCHAR(50)" in DATABASE_SCHEMA
    assert "difficulty_level VARCHAR(20)" in DATABASE_SCHEMA
    assert "estimated_duration INTEGER" in DATABASE_SCHEMA
    assert "description TEXT" in DATABASE_SCHEMA


# ============================================================
# TECHNICIAN SKILL COLUMNS
# ============================================================

def test_technician_skill_columns():

    assert "technician_id INTEGER" in DATABASE_SCHEMA
    assert "skill_id INTEGER" in DATABASE_SCHEMA
    assert "experience_years INTEGER" in DATABASE_SCHEMA
    assert "expertise_level VARCHAR(20)" in DATABASE_SCHEMA
    assert "is_verified BOOLEAN" in DATABASE_SCHEMA
    assert (
        "Primary Key:\ntechnician_id, skill_id"
        in DATABASE_SCHEMA
    )


# ============================================================
# SERVICE REQUEST COLUMNS
# ============================================================

def test_service_request_columns():

    assert "request_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "request_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "customer_id INTEGER" in DATABASE_SCHEMA
    assert "skill_id INTEGER" in DATABASE_SCHEMA
    assert "problem_description TEXT" in DATABASE_SCHEMA
    assert "priority VARCHAR(20)" in DATABASE_SCHEMA
    assert "assigned_technician_id INTEGER" in DATABASE_SCHEMA
    assert "status VARCHAR(30)" in DATABASE_SCHEMA
    assert "request_date TIMESTAMP" in DATABASE_SCHEMA


# ============================================================
# ASSIGNMENT COLUMNS
# ============================================================

def test_assignment_columns():

    assert "assignment_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "assignment_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "request_id INTEGER" in DATABASE_SCHEMA
    assert "technician_id INTEGER" in DATABASE_SCHEMA
    assert "assignment_score DECIMAL(5,2)" in DATABASE_SCHEMA
    assert "assigned_date TIMESTAMP" in DATABASE_SCHEMA


# ============================================================
# SERVICE HISTORY COLUMNS
# ============================================================

def test_service_history_columns():

    assert "history_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "history_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "request_id INTEGER" in DATABASE_SCHEMA
    assert "old_status VARCHAR(30)" in DATABASE_SCHEMA
    assert "new_status VARCHAR(30)" in DATABASE_SCHEMA
    assert "updated_time TIMESTAMP" in DATABASE_SCHEMA
    assert "remarks TEXT" in DATABASE_SCHEMA


# ============================================================
# FEEDBACK COLUMNS
# ============================================================

def test_feedback_columns():

    assert "feedback_id SERIAL PRIMARY KEY" in DATABASE_SCHEMA
    assert "feedback_uuid UUID UNIQUE" in DATABASE_SCHEMA
    assert "request_id INTEGER" in DATABASE_SCHEMA
    assert "customer_id INTEGER" in DATABASE_SCHEMA
    assert "technician_id INTEGER" in DATABASE_SCHEMA
    assert "rating DECIMAL(2,1)" in DATABASE_SCHEMA
    assert "comments TEXT" in DATABASE_SCHEMA
    assert "feedback_date TIMESTAMP" in DATABASE_SCHEMA


# ============================================================
# RELATIONSHIPS
# ============================================================

def test_relationships_section():

    assert "RELATIONSHIPS:" in DATABASE_SCHEMA


def test_customer_service_request_relationship():

    assert (
        "customers.customer_id\n=\nservice_requests.customer_id"
        in DATABASE_SCHEMA
    )


def test_skill_service_request_relationship():

    assert (
        "skills.skill_id\n=\nservice_requests.skill_id"
        in DATABASE_SCHEMA
    )


def test_technician_service_request_relationship():

    assert (
        "technicians.technician_id\n=\n"
        "service_requests.assigned_technician_id"
        in DATABASE_SCHEMA
    )


def test_technician_skill_relationship():

    assert (
        "technicians.technician_id\n=\n"
        "technician_skills.technician_id"
        in DATABASE_SCHEMA
    )


def test_skill_technician_skill_relationship():

    assert (
        "skills.skill_id\n=\ntechnician_skills.skill_id"
        in DATABASE_SCHEMA
    )


def test_assignment_request_relationship():

    assert (
        "service_requests.request_id\n=\n"
        "assignments.request_id"
        in DATABASE_SCHEMA
    )


def test_assignment_technician_relationship():

    assert (
        "technicians.technician_id\n=\n"
        "assignments.technician_id"
        in DATABASE_SCHEMA
    )


def test_history_request_relationship():

    assert (
        "service_requests.request_id\n=\n"
        "service_history.request_id"
        in DATABASE_SCHEMA
    )


def test_feedback_request_relationship():

    assert (
        "service_requests.request_id\n=\n"
        "feedback.request_id"
        in DATABASE_SCHEMA
    )


def test_feedback_customer_relationship():

    assert (
        "customers.customer_id\n=\nfeedback.customer_id"
        in DATABASE_SCHEMA
    )


def test_feedback_technician_relationship():

    assert (
        "technicians.technician_id\n=\nfeedback.technician_id"
        in DATABASE_SCHEMA
    )


# ============================================================
# BUSINESS MEANINGS
# ============================================================

def test_business_meanings_section():

    assert "BUSINESS MEANINGS" in DATABASE_SCHEMA


def test_customer_business_meaning():

    assert '"customer" means a record in customers.' in DATABASE_SCHEMA


def test_technician_business_meaning():

    assert '"technician" means a record in technicians.' in DATABASE_SCHEMA


def test_service_business_meaning():

    assert '"service" means a record in skills.' in DATABASE_SCHEMA


def test_service_request_business_meaning():

    assert (
        '"service request" means a record in service_requests.'
        in DATABASE_SCHEMA
    )


def test_technician_skill_business_meaning():

    assert (
        '"technician skill" means a record in technician_skills.'
        in DATABASE_SCHEMA
    )


def test_assignment_business_meaning():

    assert (
        '"assignment" means a record in assignments.'
        in DATABASE_SCHEMA
    )


def test_service_history_business_meaning():

    assert (
        '"service history" means a record in service_history.'
        in DATABASE_SCHEMA
    )


def test_feedback_business_meaning():

    assert (
        '"feedback" means a record in feedback.'
        in DATABASE_SCHEMA
    )


def test_rating_business_meaning():

    assert '"rating" may refer to technicians.rating' in DATABASE_SCHEMA
    assert "feedback.rating depending on the question." in DATABASE_SCHEMA


def test_available_technician_business_meaning():

    assert (
        '"available technician" means technicians'
        in DATABASE_SCHEMA
    )


def test_available_technicians_business_meaning():

    assert (
        '"available technicians" means technicians'
        in DATABASE_SCHEMA
    )

    assert (
        "availability = 'Available'"
        in DATABASE_SCHEMA
    )


def test_verified_technicians_business_meaning():

    assert (
        '"verified technicians" means technicians whose'
        in DATABASE_SCHEMA
    )

    assert "is_verified = TRUE" in DATABASE_SCHEMA


def test_technician_rating_business_meaning():

    assert (
        '"technician rating" means technicians.rating.'
        in DATABASE_SCHEMA
    )


def test_customer_rating_business_meaning():

    assert (
        '"customer rating" or "feedback rating" means feedback.rating.'
        in DATABASE_SCHEMA
    )


def test_pending_requests_business_meaning():

    assert (
        '"pending requests" means service_requests'
        in DATABASE_SCHEMA
    )


def test_completed_requests_business_meaning():

    assert (
        '"completed requests" means service_requests'
        in DATABASE_SCHEMA
    )


def test_open_requests_business_meaning():

    assert (
        '"open requests" means service_requests'
        in DATABASE_SCHEMA
    )


def test_in_progress_requests_business_meaning():

    assert (
        '"in-progress requests" means service_requests'
        in DATABASE_SCHEMA
    )


def test_highest_rated_technician_business_meaning():

    assert (
        '"highest rated technician" means technicians ordered'
        in DATABASE_SCHEMA
    )

    assert "rating descending" in DATABASE_SCHEMA


def test_lowest_rated_technician_business_meaning():

    assert (
        '"lowest rated technician" means technicians ordered'
        in DATABASE_SCHEMA
    )

    assert "rating ascending" in DATABASE_SCHEMA


# ============================================================
# COUNT MEANINGS
# ============================================================

def test_number_of_customers():

    assert (
        '"number of customers" means COUNT(*) from  customers.'
        in DATABASE_SCHEMA
    )


def test_number_of_technicians():

    assert (
        '"number of technicians" means COUNT(*) from  technicians.'
        in DATABASE_SCHEMA
    )


def test_number_of_services():

    assert (
        '"number of services" means COUNT(*) from  skills.'
        in DATABASE_SCHEMA
    )


def test_number_of_service_requests():

    assert (
        '"number of service requests" means COUNT(*) from  '
        "service_requests."
        in DATABASE_SCHEMA
    )