
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from pydantic import ValidationError

from main import app
from config import Settings

from Api.jwt import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    verify_access_token,
)

from Api.security import (
    hash_password,
    verify_password,
)

from Api.dependencies import get_current_user

from modules.auth import (
    register_customer_user,
    register_technician_user,
    authenticate_customer,
    authenticate_technician,
)

from tests.mocks.session_mock import (
    ResultMock,
    SessionMock,
)


client = TestClient(app)


# ============================================================
# CUSTOMER REGISTRATION - SERVICE
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.hash_password")
def test_register_customer_user(mock_hash_password, mock_session):
    mock_session.return_value = SessionMock()
    mock_hash_password.return_value = "hashed_password"

    data = SimpleNamespace(
        customer_name="Test User",
        phone="9876543210",
        password="Password@123",
        city="Hyderabad",
        area="Madhapur",
        pincode="500081",
    )

    actual_response = register_customer_user(data)

    assert actual_response.customer_name == "Test User"
    assert actual_response.phone == "9876543210"
    assert actual_response.password_hash == "hashed_password"


# ============================================================
# CUSTOMER REGISTRATION - DUPLICATE
# ============================================================

@patch("modules.auth.get_session_context")
def test_register_customer_duplicate(mock_session):
    existing_customer = SimpleNamespace(
        customer_id=1,
        phone="9876543210",
    )

    mock_session.return_value = SessionMock(
        result=existing_customer,
    )

    data = SimpleNamespace(
        customer_name="Test User",
        phone="9876543210",
        password="Password@123",
        city="Hyderabad",
        area="Madhapur",
        pincode="500081",
    )

    with pytest.raises(ValueError) as exc_info:
        register_customer_user(data)

    assert str(exc_info.value) == (
        "Customer with this phone number already exists."
    )


# ============================================================
# TECHNICIAN REGISTRATION - SERVICE
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.hash_password")
def test_register_technician_user(mock_hash_password, mock_session):
    # First query: no duplicate technician.
    # Second query: the requested skill exists.
    skill = SimpleNamespace(skill_id=1)

    mock_session.return_value = SessionMock(
        results=[None, skill],
    )
    mock_hash_password.return_value = "hashed_password"

    data = SimpleNamespace(
        technician_name="Test Technician",
        phone="9876543211",
        password="Password@123",
        city="Hyderabad",
        area="Madhapur",
        pincode="500081",
        skills=[
            SimpleNamespace(
                skill_id=1,
                experience_years=2,
                expertise_level="Intermediate",
            )
        ],
    )

    actual_response = register_technician_user(data)

    assert actual_response.technician_name == "Test Technician"
    assert actual_response.phone == "9876543211"
    assert actual_response.password_hash == "hashed_password"


# ============================================================
# TECHNICIAN REGISTRATION - DUPLICATE
# ============================================================

@patch("modules.auth.get_session_context")
def test_register_technician_duplicate(mock_session):
    existing_technician = SimpleNamespace(
        technician_id=1,
        phone="9876543211",
    )

    mock_session.return_value = SessionMock(
        result=existing_technician,
    )

    data = SimpleNamespace(
        technician_name="Test Technician",
        phone="9876543211",
        password="Password@123",
        city="Hyderabad",
        area="Madhapur",
        pincode="500081",
        skills=[
            SimpleNamespace(
                skill_id=1,
                experience_years=2,
                expertise_level="Intermediate",
            )
        ],
    )

    with pytest.raises(ValueError) as exc_info:
        register_technician_user(data)

    assert str(exc_info.value) == (
        "Technician with this phone number already exists."
    )


# ============================================================
# CUSTOMER AUTHENTICATION - SUCCESS
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.verify_password")
def test_authenticate_customer_success(
    mock_verify_password,
    mock_session,
):
    customer = SimpleNamespace(
        customer_uuid=uuid4(),
        phone="9876543210",
        password_hash="hashed_password",
        last_login_at=None,
    )

    mock_session.return_value = SessionMock(result=customer)
    mock_verify_password.return_value = True

    actual_response = authenticate_customer(
        "9876543210",
        "Password@123",
    )

    assert actual_response == (customer, True)
    assert customer.last_login_at is not None


# ============================================================
# CUSTOMER AUTHENTICATION - USER NOT FOUND
# ============================================================

@patch("modules.auth.get_session_context")
def test_authenticate_customer_not_found(mock_session):
    mock_session.return_value = SessionMock(result=None)

    actual_response = authenticate_customer(
        "9876543210",
        "Password@123",
    )

    assert actual_response is None


# ============================================================
# CUSTOMER AUTHENTICATION - WRONG PASSWORD
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.verify_password")
def test_authenticate_customer_wrong_password(
    mock_verify_password,
    mock_session,
):
    customer = SimpleNamespace(
        customer_uuid=uuid4(),
        phone="9876543210",
        password_hash="hashed_password",
        last_login_at=None,
    )

    mock_session.return_value = SessionMock(result=customer)
    mock_verify_password.return_value = False

    actual_response = authenticate_customer(
        "9876543210",
        "WrongPassword",
    )

    assert actual_response is None
    assert customer.last_login_at is None


# ============================================================
# TECHNICIAN AUTHENTICATION - SUCCESS
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.verify_password")
def test_authenticate_technician_success(
    mock_verify_password,
    mock_session,
):
    technician = SimpleNamespace(
        technician_uuid=uuid4(),
        phone="9876543211",
        password_hash="hashed_password",
        last_login_at=None,
    )

    mock_session.return_value = SessionMock(result=technician)
    mock_verify_password.return_value = True

    actual_response = authenticate_technician(
        "9876543211",
        "Password@123",
    )

    assert actual_response == (technician, True)
    assert technician.last_login_at is not None


# ============================================================
# TECHNICIAN AUTHENTICATION - USER NOT FOUND
# ============================================================

@patch("modules.auth.get_session_context")
def test_authenticate_technician_not_found(mock_session):
    mock_session.return_value = SessionMock(result=None)

    actual_response = authenticate_technician(
        "9876543211",
        "Password@123",
    )

    assert actual_response is None


# ============================================================
# TECHNICIAN AUTHENTICATION - WRONG PASSWORD
# ============================================================

@patch("modules.auth.get_session_context")
@patch("modules.auth.verify_password")
def test_authenticate_technician_wrong_password(
    mock_verify_password,
    mock_session,
):
    technician = SimpleNamespace(
        technician_uuid=uuid4(),
        phone="9876543211",
        password_hash="hashed_password",
        last_login_at=None,
    )

    mock_session.return_value = SessionMock(result=technician)
    mock_verify_password.return_value = False

    actual_response = authenticate_technician(
        "9876543211",
        "WrongPassword",
    )

    assert actual_response is None
    assert technician.last_login_at is None


# ============================================================
# API - CUSTOMER REGISTRATION - SUCCESS
# ============================================================

@patch("Api.auth.register_customer_user")
def test_customer_register_api_success(mock_register_customer):
    customer_uuid = uuid4()

    mock_register_customer.return_value = SimpleNamespace(
        customer_uuid=customer_uuid,
    )

    response = client.post(
        "/auth/register/customer",
        json={
            "customer_name": "Test User",
            "phone": "9876543210",
            "password": "Password@123",
            "city": "Hyderabad",
            "area": "Madhapur",
            "pincode": "500081",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Customer registered successfully.",
        "customer_uuid": str(customer_uuid),
    }


# ============================================================
# API - CUSTOMER REGISTRATION - FAILURE
# ============================================================

@patch("Api.auth.register_customer_user")
def test_customer_register_api_failure(mock_register_customer):
    mock_register_customer.side_effect = ValueError(
        "Customer with this phone number already exists."
    )

    response = client.post(
        "/auth/register/customer",
        json={
            "customer_name": "Test User",
            "phone": "9876543210",
            "password": "Password@123",
            "city": "Hyderabad",
            "area": "Madhapur",
            "pincode": "500081",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Customer with this phone number already exists."
    }


# ============================================================
# API - TECHNICIAN REGISTRATION - SUCCESS
# ============================================================

@patch("Api.auth.register_technician_user")
def test_technician_register_api_success(mock_register_technician):
    technician_uuid = uuid4()

    mock_register_technician.return_value = SimpleNamespace(
        technician_uuid=technician_uuid,
    )

    response = client.post(
        "/auth/register/technician",
        json={
            "technician_name": "Test Technician",
            "phone": "9876543211",
            "password": "Password@123",
            "city": "Hyderabad",
            "area": "Madhapur",
            "pincode": "500081",
            "skills": [
                {
                    "skill_id": 1,
                    "experience_years": 2,
                    "expertise_level": "Intermediate",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Technician registered successfully.",
        "technician_uuid": str(technician_uuid),
    }


# ============================================================
# API - TECHNICIAN REGISTRATION - FAILURE
# ============================================================

@patch("Api.auth.register_technician_user")
def test_technician_register_api_failure(mock_register_technician):
    mock_register_technician.side_effect = ValueError(
        "Technician with this phone number already exists."
    )

    response = client.post(
        "/auth/register/technician",
        json={
            "technician_name": "Test Technician",
            "phone": "9876543211",
            "password": "Password@123",
            "city": "Hyderabad",
            "area": "Madhapur",
            "pincode": "500081",
            "skills": [
                {
                    "skill_id": 1,
                    "experience_years": 2,
                    "expertise_level": "Intermediate",
                }
            ],
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Technician with this phone number already exists."
    }


# ============================================================
# API - CUSTOMER LOGIN - SUCCESS
# ============================================================

@patch("Api.auth.create_access_token")
@patch("Api.auth.authenticate_customer")
def test_customer_login_api_success(
    mock_authenticate_customer,
    mock_create_access_token,
):
    customer_uuid = uuid4()

    customer = SimpleNamespace(
        customer_uuid=customer_uuid,
        customer_name="Test User",
    )

    mock_authenticate_customer.return_value = (customer, False)
    mock_create_access_token.return_value = "test-customer-token"

    response = client.post(
        "/auth/login/customer",
        json={
            "phone": "9876543210",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-customer-token",
        "token_type": "bearer",
        "user_uuid": str(customer_uuid),
        "name": "Test User",
        "role": "customer",
        "first_login": False,
    }


# ============================================================
# API - CUSTOMER LOGIN - FAILURE
# ============================================================

@patch("Api.auth.authenticate_customer")
def test_customer_login_api_failure(mock_authenticate_customer):
    mock_authenticate_customer.return_value = None

    response = client.post(
        "/auth/login/customer",
        json={
            "phone": "9876543210",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid phone number or password."
    }


# ============================================================
# API - TECHNICIAN LOGIN - SUCCESS
# ============================================================

@patch("Api.auth.create_access_token")
@patch("Api.auth.authenticate_technician")
def test_technician_login_api_success(
    mock_authenticate_technician,
    mock_create_access_token,
):
    technician_uuid = uuid4()

    technician = SimpleNamespace(
        technician_uuid=technician_uuid,
        technician_name="Test Technician",
    )

    mock_authenticate_technician.return_value = (technician, False)
    mock_create_access_token.return_value = "test-technician-token"

    response = client.post(
        "/auth/login/technician",
        json={
            "phone": "9876543211",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-technician-token",
        "token_type": "bearer",
        "user_uuid": str(technician_uuid),
        "name": "Test Technician",
        "role": "technician",
        "first_login": False,
    }


# ============================================================
# API - TECHNICIAN LOGIN - FAILURE
# ============================================================

@patch("Api.auth.authenticate_technician")
def test_technician_login_api_failure(mock_authenticate_technician):
    mock_authenticate_technician.return_value = None

    response = client.post(
        "/auth/login/technician",
        json={
            "phone": "9876543211",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid phone number or password."
    }


# ============================================================
# SECURITY - HASH PASSWORD
# ============================================================

def test_hash_password():
    password = "Password@123"
    actual_hash = hash_password(password)

    assert actual_hash != password
    assert isinstance(actual_hash, str)
    assert len(actual_hash) > 0


# ============================================================
# SECURITY - VERIFY PASSWORD SUCCESS
# ============================================================

def test_verify_password_success():
    password = "Password@123"
    password_hash = hash_password(password)

    actual_result = verify_password(password, password_hash)

    assert actual_result is True


# ============================================================
# SECURITY - VERIFY PASSWORD FAILURE
# ============================================================

def test_verify_password_failure():
    password_hash = hash_password("Password@123")

    actual_result = verify_password(
        "WrongPassword@123",
        password_hash,
    )

    assert actual_result is False


# ============================================================
# JWT - CREATE TOKEN
# ============================================================

def test_create_access_token():
    customer_uuid = uuid4()

    data = {
        "sub": str(customer_uuid),
        "role": "customer",
    }

    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = verify_access_token(token)

    assert payload["sub"] == str(customer_uuid)
    assert payload["role"] == "customer"
    assert "exp" in payload


# ============================================================
# JWT - ORIGINAL DATA NOT MODIFIED
# ============================================================

def test_create_access_token_original_data_not_modified():
    data = {
        "sub": "test-user",
        "role": "customer",
    }

    original_data = data.copy()
    create_access_token(data)

    assert data == original_data


# ============================================================
# JWT - INVALID TOKEN
# ============================================================

def test_verify_access_token_invalid():
    actual_response = verify_access_token("invalid.jwt.token")

    assert actual_response is None


# ============================================================
# JWT - EXPIRED TOKEN
# ============================================================

def test_verify_access_token_expired():
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)

    expired_token = jwt.encode(
        {
            "sub": "test-user",
            "role": "customer",
            "exp": expired_time,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    actual_response = verify_access_token(expired_token)

    assert actual_response is None


# ============================================================
# DEPENDENCY - VALID TOKEN
# ============================================================

def test_get_current_user_success():
    user_uuid = str(uuid4())

    payload = {
        "sub": user_uuid,
        "role": "customer",
    }

    with patch(
        "Api.dependencies.verify_access_token",
        return_value=payload,
    ):
        actual_response = get_current_user(
            SimpleNamespace(credentials="valid-token")
        )

    assert actual_response == {
        "user_uuid": user_uuid,
        "role": "customer",
    }


# ============================================================
# DEPENDENCY - INVALID TOKEN
# ============================================================

def test_get_current_user_invalid_token():
    with patch(
        "Api.dependencies.verify_access_token",
        return_value=None,
    ):
        with pytest.raises(Exception) as exc_info:
            get_current_user(
                SimpleNamespace(credentials="invalid-token")
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token."
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


# ============================================================
# DEPENDENCY - MISSING USER UUID
# ============================================================

def test_get_current_user_missing_user_uuid():
    payload = {"role": "customer"}

    with patch(
        "Api.dependencies.verify_access_token",
        return_value=payload,
    ):
        with pytest.raises(Exception) as exc_info:
            get_current_user(
                SimpleNamespace(credentials="valid-token")
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token payload."
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


# ============================================================
# DEPENDENCY - MISSING ROLE
# ============================================================

def test_get_current_user_missing_role():
    payload = {"sub": str(uuid4())}

    with patch(
        "Api.dependencies.verify_access_token",
        return_value=payload,
    ):
        with pytest.raises(Exception) as exc_info:
            get_current_user(
                SimpleNamespace(credentials="valid-token")
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token payload."
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


# ============================================================
# SESSION MOCK - RESULT FIRST
# ============================================================

def test_result_mock_first():
    result = ResultMock("test-result")

    assert result.first() == "test-result"


# ============================================================
# SESSION MOCK - RESULT ALL
# ============================================================

def test_result_mock_all_with_result():
    result = ResultMock(["item1", "item2"])

    assert result.all() == ["item1", "item2"]


# ============================================================
# SESSION MOCK - RESULT ALL EMPTY
# ============================================================

def test_result_mock_all_without_result():
    result = ResultMock()

    assert result.all() == []


# ============================================================
# SESSION MOCK - CONTEXT MANAGER
# ============================================================

def test_session_mock_context_manager():
    session = SessionMock()

    with session as active_session:
        assert active_session is session

    assert session.__exit__() is None


# ============================================================
# SESSION MOCK - ADD
# ============================================================

def test_session_mock_add():
    session = SessionMock()
    obj = SimpleNamespace(id=1)

    assert session.add(obj) is None


# ============================================================
# SESSION MOCK - COMMIT
# ============================================================

def test_session_mock_commit():
    session = SessionMock()

    assert session.commit() is None


# ============================================================
# SESSION MOCK - REFRESH
# ============================================================

def test_session_mock_refresh():
    session = SessionMock()
    obj = SimpleNamespace(id=1)

    assert session.refresh(obj) is None


# ============================================================
# SESSION MOCK - GET
# ============================================================

def test_session_mock_get():
    expected_object = SimpleNamespace(id=1)
    session = SessionMock(get_result=expected_object)

    actual_object = session.get(None, 1)

    assert actual_object is expected_object


# ============================================================
# SESSION MOCK - EXEC SINGLE RESULT
# ============================================================

def test_session_mock_exec_single_result():
    session = SessionMock(result="single-result")
    result = session.exec("query")

    assert result.first() == "single-result"
    assert result.all() == "single-result"


# ============================================================
# SESSION MOCK - EXEC MULTIPLE RESULTS
# ============================================================

def test_session_mock_exec_multiple_results():
    session = SessionMock(
        results=["first-result", "second-result"],
    )

    result1 = session.exec("query1")
    result2 = session.exec("query2")

    assert result1.first() == "first-result"
    assert result2.first() == "second-result"
    assert session.exec_count == 2


# ============================================================
# SETTINGS - JWT SECRET KEY NOT CONFIGURED
# ============================================================

def test_jwt_secret_key_missing():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql://example",
            OPENROUTER_API_KEY="test-key",
        )

    errors = exc_info.value.errors()

    assert any(
        "JWT_SECRET_KEY" in error["loc"]
        for error in errors
    )
