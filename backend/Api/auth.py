from Log_config import log

from fastapi import APIRouter, HTTPException

from Api.schemas import (
    CustomerRegister,
    TechnicianRegister,
    LoginRequest,
    TokenResponse,
    CustomerRegisterResponse,
    TechnicianRegisterResponse
)

from Api.jwt import create_access_token

from modules.auth import (
    register_customer_user,
    register_technician_user,
    authenticate_customer,
    authenticate_technician
)


logger = log()


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# CUSTOMER REGISTRATION
# ============================================================

@router.post(
    "/register/customer",
    response_model=CustomerRegisterResponse
)
def register_customer(data: CustomerRegister):

    logger.info(
        "Customer registration request received | phone: %s",
        data.phone
    )

    try:
        customer = register_customer_user(data)

    except ValueError as error:
        logger.warning(
            "Customer registration failed | phone: %s | reason: %s",
            data.phone,
            error
        )

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    logger.info(
        "Customer registered successfully | customer_uuid: %s",
        customer.customer_uuid
    )

    return {
        "message": "Customer registered successfully.",
        "customer_uuid": customer.customer_uuid
    }


# ============================================================
# TECHNICIAN REGISTRATION
# ============================================================

@router.post(
    "/register/technician",
    response_model=TechnicianRegisterResponse
)
def register_technician(data: TechnicianRegister):

    logger.info(
        "Technician registration request received | phone: %s",
        data.phone
    )

    try:
        technician = register_technician_user(data)

    except ValueError as error:
        logger.warning(
            "Technician registration failed | phone: %s | reason: %s",
            data.phone,
            error
        )

        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    logger.info(
        "Technician registered successfully | technician_uuid: %s",
        technician.technician_uuid
    )

    return {
        "message": "Technician registered successfully.",
        "technician_uuid": technician.technician_uuid
    }


# ============================================================
# CUSTOMER LOGIN
# ============================================================

@router.post(
    "/login/customer",
    response_model=TokenResponse
)
def login_customer(data: LoginRequest):

    logger.info(
        "Customer login attempt | phone: %s",
        data.phone
    )

    authentication_result = authenticate_customer(
        data.phone,
        data.password
    )

    if authentication_result is None:
        logger.warning(
            "Customer login failed | phone: %s",
            data.phone
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password."
        )

    customer, first_login = authentication_result

    access_token = create_access_token({
        "sub": str(customer.customer_uuid),
        "role": "customer"
    })

    logger.info(
        "Customer login successful | customer_uuid: %s | first_login: %s",
        customer.customer_uuid,
        first_login
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_uuid": customer.customer_uuid,
        "name": customer.customer_name,
        "role": "customer",
        "first_login": first_login
    }


# ============================================================
# TECHNICIAN LOGIN
# ============================================================

@router.post(
    "/login/technician",
    response_model=TokenResponse
)
def login_technician(data: LoginRequest):

    logger.info(
        "Technician login attempt | phone: %s",
        data.phone
    )

    authentication_result = authenticate_technician(
        data.phone,
        data.password
    )

    if authentication_result is None:
        logger.warning(
            "Technician login failed | phone: %s",
            data.phone
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password."
        )

    technician, first_login = authentication_result

    access_token = create_access_token({
        "sub": str(technician.technician_uuid),
        "role": "technician"
    })

    logger.info(
        "Technician login successful | technician_uuid: %s | first_login: %s",
        technician.technician_uuid,
        first_login
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_uuid": technician.technician_uuid,
        "name": technician.technician_name,
        "role": "technician",
        "first_login": first_login
    }
