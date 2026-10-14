from io import BytesIO

from Log_config import log

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from Api.dependencies import get_current_user

from Api.schemas import (
    ReportsResponse,
    CustomerReportsResponse
)

from modules.reports_service import (
    get_reports,
    get_customer_reports
)


logger = log()


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ============================================================
# TECHNICIAN REPORTS
# ============================================================

@router.get(
    "",
    response_model=ReportsResponse
)
def view_reports(
    current_user=Depends(get_current_user)
):

    logger.info(
        "View reports attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "technician":

        logger.warning(
            "View reports denied | "
            "user_uuid: %s | role: %s",
            current_user["user_uuid"],
            current_user["role"]
        )

        raise HTTPException(
            status_code=403,
            detail="Only technicians can view reports."
        )

    reports = get_reports()

    logger.info(
        "Reports retrieved successfully | "
        "technician_uuid: %s",
        current_user["user_uuid"]
    )

    return reports


# ============================================================
# TECHNICIAN PDF REPORT DOWNLOAD
# ============================================================

@router.get(
    "/pdf"
)
def download_technician_reports_pdf(
    current_user=Depends(get_current_user)
):

    logger.info(
        "Technician PDF download attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "technician":
        raise HTTPException(
            status_code=403,
            detail="Only technicians can download reports."
        )

    reports_data = get_reports()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TechnicianReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=16
    )

    story = [
        Paragraph(
            "Service Dispatch Analytics Report",
            title_style
        )
    ]

    # Support both dictionary and Pydantic model responses.
    if hasattr(reports_data, "model_dump"):
        reports_data = reports_data.model_dump()
    elif not isinstance(reports_data, dict):
        reports_data = dict(reports_data)

    def add_section(section_title, section_data):
        story.append(
            Paragraph(
                escape(section_title),
                styles["Heading2"]
            )
        )

        if hasattr(section_data, "model_dump"):
            section_data = section_data.model_dump()

        if isinstance(section_data, dict):
            table_data = [["Metric", "Value"]]

            for key, value in section_data.items():
                if isinstance(value, dict):
                    value = ", ".join(
                        f"{nested_key}: {nested_value}"
                        for nested_key, nested_value in value.items()
                    )

                table_data.append([
                    Paragraph(
                        escape(str(key.replace("_", " ").title())),
                        styles["Normal"]
                    ),
                    Paragraph(
                        escape(str(value if value is not None else "N/A")),
                        styles["Normal"]
                    )
                ])

            table = Table(
                table_data,
                colWidths=[55 * mm, 105 * mm],
                repeatRows=1
            )

            table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND", (0, 0), (-1, 0),
                        colors.HexColor("#1D4ED8")
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "BACKGROUND", (0, 1), (0, -1),
                        colors.HexColor("#EFF6FF")
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
                ])
            )

            story.append(table)
            story.append(Spacer(1, 6 * mm))

        elif isinstance(section_data, list):
            for item in section_data:
                if hasattr(item, "model_dump"):
                    item = item.model_dump()

                if isinstance(item, dict):
                    add_section("Technician Details", item)

    for section_name, section_data in reports_data.items():
        add_section(
            section_name.replace("_", " ").title(),
            section_data
        )

    document.build(story)

    buffer.seek(0)

    logger.info(
        "Technician PDF generated | user_uuid: %s",
        current_user["user_uuid"]
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="technician_analytics_report.pdf"'
            ),
            "Cache-Control": "no-store"
        }
    )


# ============================================================
# CUSTOMER REPORTS
# ============================================================

@router.get(
    "/customer",
    response_model=CustomerReportsResponse
)
def view_customer_reports(
    current_user=Depends(get_current_user)
):

    logger.info(
        "Customer reports attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can view customer reports."
        )

    reports = get_customer_reports(
        current_user["user_uuid"]
    )

    if reports is None:
        raise HTTPException(
            status_code=404,
            detail="Customer account not found."
        )

    logger.info(
        "Customer reports retrieved | "
        "user_uuid: %s | count: %s",
        current_user["user_uuid"],
        reports["count"]
    )

    return reports


# ============================================================
# CUSTOMER PDF REPORT DOWNLOAD
# ============================================================

@router.get(
    "/customer/pdf"
)
def download_customer_reports_pdf(
    current_user=Depends(get_current_user)
):

    logger.info(
        "Customer PDF download attempt | "
        "user_uuid: %s | role: %s",
        current_user["user_uuid"],
        current_user["role"]
    )

    if current_user["role"] != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can download customer reports."
        )

    reports_data = get_customer_reports(
        current_user["user_uuid"]
    )

    if reports_data is None:
        raise HTTPException(
            status_code=404,
            detail="Customer account not found."
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomerReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=12
    )

    story = [
        Paragraph(
            "Customer Service Reports",
            title_style
        ),
        Paragraph(
            f"Total service requests: {reports_data['count']}",
            styles["Normal"]
        ),
        Spacer(1, 8 * mm)
    ]

    for index, report in enumerate(
        reports_data["reports"],
        start=1
    ):

        technician = report.get("technician")

        technician_name = (
            technician["technician_name"]
            if technician
            else "Not assigned"
        )

        request_date = report["request_date"]

        if hasattr(request_date, "strftime"):
            request_date = request_date.strftime(
                "%d-%m-%Y %H:%M"
            )

        # Escape user-provided text before inserting it into a PDF paragraph.
        from xml.sax.saxutils import escape

        table_data = [
            ["Field", "Details"],
            ["Request", str(index)],
            ["Request ID", str(report["request_uuid"])],
            ["Service", Paragraph(
                escape(str(report["service"])),
                styles["Normal"]
            )],
            ["Problem", Paragraph(
                escape(str(report["problem_description"])),
                styles["Normal"]
            )],
            ["Priority", str(
                report["priority"] or "Not specified"
            )],
            ["Status", str(report["status"])],
            ["Request date", str(request_date)],
            ["Technician", escape(str(technician_name))]
        ]

        table = Table(
            table_data,
            colWidths=[35 * mm, 125 * mm],
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1D4ED8")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.lightgrey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (0, -1),
                    colors.HexColor("#EFF6FF")
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(table)
        story.append(Spacer(1, 7 * mm))

    document.build(story)

    buffer.seek(0)

    logger.info(
        "Customer PDF generated | "
        "customer_uuid: %s | count: %s",
        current_user["user_uuid"],
        reports_data["count"]
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="customer_service_reports.pdf"'
            ),
            "Cache-Control": "no-store"
        }
    )
