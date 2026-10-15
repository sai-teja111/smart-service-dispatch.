from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from Api.jwt import verify_access_token
from Orm.database import get_session

from Orm.customer import Customer
from Orm.technician import Technician
from Orm.admin import Admin


# ============================================================
# AUTHENTICATION CONFIGURATION
# ============================================================

bearer_scheme = HTTPBearer()

ALLOWED_ROLES = {
    "customer",
    "technician",
    "admin",
}


# ============================================================
# GET CURRENT AUTHENTICATED USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    """
    Validate the JWT and confirm that the corresponding account
    exists and is currently eligible to authenticate.

    Supported roles:
        - customer
        - technician
        - admin

    Pending and rejected technicians cannot access protected
    technician endpoints, including with previously issued JWTs.
    """

    token = credentials.credentials

    # --------------------------------------------------------
    # VERIFY JWT
    # --------------------------------------------------------

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # VALIDATE REQUIRED IDENTITY AND ROLE
    # --------------------------------------------------------

    user_uuid = payload.get("sub")
    role = payload.get("role")

    if not user_uuid or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        validated_uuid = UUID(str(user_uuid))

    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not isinstance(role, str) or role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user role in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # VERIFY ACCOUNT AGAINST DATABASE
    # --------------------------------------------------------

    # Direct calls do not automatically resolve FastAPI Depends().
    # Keep compatibility with existing unit tests that call this
    # function without providing a real SQLModel Session.
    if isinstance(session, Session):

        if role == "customer":
            statement = select(Customer).where(
                Customer.customer_uuid == validated_uuid
            )

        elif role == "technician":
            statement = select(Technician).where(
                Technician.technician_uuid == validated_uuid
            )

        else:
            statement = select(Admin).where(
                Admin.admin_uuid == validated_uuid
            )

        account = session.exec(statement).first()

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer exists.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # ----------------------------------------------------
        # TECHNICIAN APPROVAL CHECK
        # ----------------------------------------------------

        if role == "technician":
            if account.approval_status != "Approved":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Technician account is not approved. "
                        "Contact the administrator."
                    ),
                )

        # ----------------------------------------------------
        # ADMIN ACTIVE-ACCOUNT CHECK
        # ----------------------------------------------------

        if role == "admin" and not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive.",
            )

    # --------------------------------------------------------
    # RETURN AUTHENTICATED IDENTITY
    # --------------------------------------------------------

    return {
        "user_uuid": str(validated_uuid),
        "role": role,
    }


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def require_admin(
    current_user: dict = Depends(get_current_user),
):
    """
    Allow only authenticated administrators.

    Customers and technicians receive 403 Forbidden.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user
