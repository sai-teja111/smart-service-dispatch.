
from fastapi import Depends, HTTPException, status

from Api.dependencies import get_current_user


def require_customer(
    current_user: dict = Depends(get_current_user),
):
    """
    Allow access only to authenticated customers.
    """
    if current_user["role"] != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required.",
        )

    return current_user


def require_technician(
    current_user: dict = Depends(get_current_user),
):
    """
    Allow access only to authenticated technicians.
    """
    if current_user["role"] != "technician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technician access required.",
        )

    return current_user
