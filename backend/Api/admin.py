from io import BytesIO
from typing import Literal
from uuid import UUID
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from Log_config import log

from Api.admin_schemas import AdminLogin
from Api.dependencies import require_admin

from modules.admin_service import (
    login_admin,
    get_admin_by_uuid,
    get_all_customers,
    get_customer_by_uuid,
    get_customer_service_requests,
    get_customer_report,
    get_technician_report,
    get_admin_report_summary,
    get_all_technicians,
    get_pending_technicians,
    update_technician_approval,
    get_all_technician_skills,
    get_pending_technician_skills,
    update_technician_skill_verification,
)


logger = log()

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class TechnicianApprovalRequest(BaseModel):
    approval_status: Literal["Approved", "Rejected"]


class TechnicianSkillVerificationRequest(BaseModel):
    is_verified: bool


# ============================================================
# PDF REPORT HELPER
# ============================================================

def generate_report_pdf(
    title: str,
    rows: list,
    preferred_columns: list[str],
) -> bytes:
    """
    Generate a PDF report from the existing report service data.

    The original report data is not modified.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AdminReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=8,
    )

    cell_style = ParagraphStyle(
        "AdminReportCell",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        wordWrap="CJK",
    )

    header_style = ParagraphStyle(
        "AdminReportHeader",
        parent=cell_style,
        textColor=colors.white,
        fontName="Helvetica-Bold",
    )

    story = [
        Paragraph(escape(title), title_style),
        Spacer(1, 4 * mm),
    ]

    # Show a useful message when there are no report records.
    if not rows:
        story.append(
            Paragraph(
                "No records available for this report.",
                styles["Normal"],
            )
        )

        document.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    # Convert returned records into dictionaries.
    normalized_rows = []

    for item in rows:
        if isinstance(item, dict):
            row = item
        elif hasattr(item, "model_dump"):
            row = item.model_dump()
        elif hasattr(item, "__dict__"):
            row = {
                key: value
                for key, value in vars(item).items()
                if not key.startswith("_")
            }
        else:
            row = {"Value": str(item)}

        normalized_rows.append(row)

    # Keep the preferred report columns first when they exist.
    available_columns = list(
        dict.fromkeys(
            key
            for row in normalized_rows
            for key in row.keys()
        )
    )

    columns = [
        column
        for column in preferred_columns
        if column in available_columns
    ]

    # Preserve any additional fields returned by the service.
    columns.extend(
        column
        for column in available_columns
        if column not in columns
    )

    table_data = [
        [
            Paragraph(
                escape(str(column).replace("_", " ").title()),
                header_style,
            )
            for column in columns
        ]
    ]

    for row in normalized_rows:
        table_row = []

        for column in columns:
            value = row.get(column, "")

            if value is None:
                value = ""

            if isinstance(value, (dict, list, tuple)):
                value = str(value)

            safe_value = escape(str(value))

            table_row.append(
                Paragraph(safe_value, cell_style)
            )

        table_data.append(table_row)

    # Divide the available page width evenly among the columns.
    available_width = (
        landscape(A4)[0] - document.leftMargin - document.rightMargin
    )

    column_count = max(len(columns), 1)
    column_width = available_width / column_count

    report_table = Table(
        table_data,
        colWidths=[column_width] * column_count,
        repeatRows=1,
        hAlign="LEFT",
    )

    report_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#243B53"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9E2EC"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F0F4F8"),
                    ],
                ),
            ]
        )
    )

    story.append(report_table)

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# ============================================================
# ADMIN LOGIN
# ============================================================

@router.post("/login")
def admin_login(data: AdminLogin):
    """Authenticate the provisioned administrator."""

    logger.info("Admin login attempt received.")

    try:
        result = login_admin(data)

    except HTTPException as error:
        if error.status_code == status.HTTP_401_UNAUTHORIZED:
            logger.warning(
                "Admin login failed: invalid credentials."
            )
        elif error.status_code == status.HTTP_403_FORBIDDEN:
            logger.warning(
                "Admin login denied: inactive account."
            )
        raise

    logger.info("Admin login successful.")
    return result


# ============================================================
# GET CURRENT ADMIN PROFILE
# ============================================================

@router.get("/me")
def get_current_admin(
    current_admin: dict = Depends(require_admin),
):
    """Return the authenticated administrator's profile."""

    return get_admin_by_uuid(
        current_admin["user_uuid"]
    )


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

@router.get("/customers")
def list_customers(
    current_admin: dict = Depends(require_admin),
):
    """Return all customers for the Admin dashboard."""

    customers = get_all_customers()

    return {
        "total": len(customers),
        "customers": customers,
    }


# ============================================================
# GET ONE CUSTOMER
# ============================================================

@router.get("/customers/{customer_uuid}")
def get_customer_details(
    customer_uuid: UUID,
    current_admin: dict = Depends(require_admin),
):
    """Return the details of one customer."""

    return get_customer_by_uuid(
        customer_uuid=str(customer_uuid)
    )


# ============================================================
# GET A CUSTOMER'S SERVICE REQUESTS
# ============================================================

@router.get("/customers/{customer_uuid}/requests")
def list_customer_service_requests(
    customer_uuid: UUID,
    current_admin: dict = Depends(require_admin),
):
    """Return service requests belonging to one customer."""

    requests = get_customer_service_requests(
        customer_uuid=str(customer_uuid)
    )

    return {
        "total": len(requests),
        "requests": requests,
    }


# ============================================================
# ADMIN REPORT: CUSTOMERS
# ============================================================

@router.get("/reports/customers")
def customer_report(
    current_admin: dict = Depends(require_admin),
):
    """Return customer details and request statistics."""

    customers = get_customer_report()

    return {
        "total": len(customers),
        "customers": customers,
    }


# ============================================================
# DOWNLOAD CUSTOMER REPORT AS PDF
# ============================================================

@router.get("/reports/customers/pdf")
def download_customer_report_pdf(
    current_admin: dict = Depends(require_admin),
):
    """Download the customer report as a PDF file."""

    customers = get_customer_report()

    pdf_bytes = generate_report_pdf(
        title="Customer Report",
        rows=customers,
        preferred_columns=[
            "customer_name",
            "name",
            "full_name",
            "phone",
            "email",
            "city",
            "area",
            "pincode",
            "total_requests",
            "completed_requests",
            "outstanding_requests",
        ],
    )

    logger.info("Customer report PDF generated.")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="customer_report.pdf"'
            )
        },
    )


# ============================================================
# ADMIN REPORT: TECHNICIANS
# ============================================================

@router.get("/reports/technicians")
def technician_report(
    current_admin: dict = Depends(require_admin),
):
    """Return technician details and request statistics."""

    technicians = get_technician_report()

    return {
        "total": len(technicians),
        "technicians": technicians,
    }


# ============================================================
# DOWNLOAD TECHNICIAN REPORT AS PDF
# ============================================================

@router.get("/reports/technicians/pdf")
def download_technician_report_pdf(
    current_admin: dict = Depends(require_admin),
):
    """Download the technician report as a PDF file."""

    technicians = get_technician_report()

    pdf_bytes = generate_report_pdf(
        title="Technician Report",
        rows=technicians,
        preferred_columns=[
            "technician_name",
            "name",
            "full_name",
            "phone",
            "email",
            "city",
            "area",
            "pincode",
            "availability",
            "approval_status",
            "workload",
            "rating",
            "assigned_requests",
            "completed_requests",
            "verified_skills_count",
        ],
    )

    logger.info("Technician report PDF generated.")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="technician_report.pdf"'
            )
        },
    )


# ============================================================
# ADMIN REPORT: DASHBOARD SUMMARY
# ============================================================

@router.get("/reports/summary")
def admin_report_summary(
    current_admin: dict = Depends(require_admin),
):
    """Return overall customer, technician, and request statistics."""

    return get_admin_report_summary()


# ============================================================
# GET ALL TECHNICIANS
# ============================================================

@router.get("/technicians")
def list_technicians(
    current_admin: dict = Depends(require_admin),
):
    """Return all technicians and their approval statuses."""

    technicians = get_all_technicians()

    return {
        "total": len(technicians),
        "technicians": technicians,
    }


# ============================================================
# GET PENDING TECHNICIANS
# ============================================================

@router.get("/technicians/pending")
def list_pending_technicians(
    current_admin: dict = Depends(require_admin),
):
    """Return technicians awaiting Admin approval."""

    technicians = get_pending_technicians()

    return {
        "total": len(technicians),
        "technicians": technicians,
    }


# ============================================================
# APPROVE OR REJECT A TECHNICIAN
# ============================================================

@router.patch("/technicians/{technician_uuid}/approval")
def change_technician_approval(
    technician_uuid: UUID,
    data: TechnicianApprovalRequest,
    current_admin: dict = Depends(require_admin),
):
    """Approve or reject a technician account."""

    return update_technician_approval(
        technician_uuid=str(technician_uuid),
        approval_status=data.approval_status,
    )


# ============================================================
# GET ALL TECHNICIAN SKILLS
# ============================================================

@router.get("/technician-skills")
def list_technician_skills(
    current_admin: dict = Depends(require_admin),
):
    """Return all technician skills and verification statuses."""

    skills = get_all_technician_skills()

    return {
        "total": len(skills),
        "skills": skills,
    }


# ============================================================
# GET PENDING TECHNICIAN SKILLS
# ============================================================

@router.get("/technician-skills/pending")
def list_pending_technician_skills(
    current_admin: dict = Depends(require_admin),
):
    """Return technician skills awaiting verification."""

    skills = get_pending_technician_skills()

    return {
        "total": len(skills),
        "skills": skills,
    }


# ============================================================
# VERIFY OR UNVERIFY A TECHNICIAN SKILL
# ============================================================

@router.patch(
    "/technicians/{technician_uuid}/skills/{skill_id}/verification"
)
def change_technician_skill_verification(
    technician_uuid: UUID,
    skill_id: int,
    data: TechnicianSkillVerificationRequest,
    current_admin: dict = Depends(require_admin),
):
    """
    Verify a submitted skill or remove its verification.

    is_verified=true  -> verified
    is_verified=false -> unverified
    """

    return update_technician_skill_verification(
        technician_uuid=str(technician_uuid),
        skill_id=skill_id,
        is_verified=data.is_verified,
    )
