from sqlmodel import text

from Orm.database import get_session_context


MAX_RESULTS = 100


# ============================================================
# ROLE-AWARE HELP GUIDANCE
# ============================================================

CUSTOMER_HELP = {
    "book": (
        "To book a service:\n"
        "1. Open your Customer Dashboard.\n"
        "2. Navigate to the service request or booking section.\n"
        "3. Follow the service detection and available-service prompts.\n"
        "4. Provide the requested problem details and submit the request.\n"
        "5. Review the confirmation and any technician assignment shown.\n\n"
        "You can then use My Requests to review your request status."
    ),
    "track": (
        "To track a service request:\n"
        "1. Open your Customer Dashboard.\n"
        "2. Navigate to My Requests or Service Requests.\n"
        "3. Find your request and review its current status.\n"
        "4. Open the service history section to review status updates."
    ),
    "cancel": (
        "To ask about cancelling a service request, open your request "
        "in the Customer Dashboard and check the actions available for it. "
        "Cancellation eligibility depends on the application's implemented "
        "rules. This assistant cannot cancel requests or confirm eligibility."
    ),
    "feedback": (
        "To submit feedback, open your completed service request in the "
        "Customer Dashboard and look for the feedback option. If available, "
        "submit your rating and comments. Eligibility depends on the "
        "application's implemented rules."
    ),
    "history": (
        "To review service history, open your Customer Dashboard and navigate "
        "to Service History or the history option for a specific request. "
        "Available records may include previous statuses, update times, "
        "and remarks."
    ),
    "default": (
        "I can help you use the customer portal. Ask about booking a service, "
        "tracking requests, cancellation guidance, feedback, or service history."
    ),
}


TECHNICIAN_HELP = {
    "jobs": (
        "To view your assigned jobs:\n"
        "1. Open your Technician Dashboard.\n"
        "2. Navigate to Assigned Jobs, My Requests, or the equivalent section.\n"
        "3. Select a request to review its details and current status.\n"
        "The exact page label depends on your portal layout."
    ),
    "location": (
        "To find a customer's location, open an assigned request from your "
        "Technician Dashboard and review the customer details displayed for "
        "that request. Only access location and contact information for jobs "
        "you are authorized to handle."
    ),
    "status": (
        "To update a job's status:\n"
        "1. Open the assigned request in your Technician Dashboard.\n"
        "2. Find the status-update action, if available.\n"
        "3. Select an allowed status and provide remarks if requested.\n"
        "4. Submit the update and verify the resulting status.\n"
        "This assistant does not change request statuses itself."
    ),
    "completed": (
        "To review completed jobs, open your Technician Dashboard and look "
        "for the completed-jobs filter or My Requests section. Review each "
        "request's status to identify completed work."
    ),
    "default": (
        "I can help you use the technician portal. Ask about assigned jobs, "
        "customer location details, job-status updates, or completed work."
    ),
}


def _normalize_question(question):
    """Normalize question wording for consistent matching."""
    return " ".join(question.lower().strip().replace("-", " ").split())


def _get_help_response(question, role):
    """Return role-specific procedural guidance without accessing the database."""
    q = _normalize_question(question)

    if role == "customer":
        if any(term in q for term in (
            "book a service",
            "book service",
            "booking a service",
            "create a service request",
            "raise a service request",
            "place a service request",
            "how do i book",
            "how to book",
        )):
            return CUSTOMER_HELP["book"]

        if any(term in q for term in (
            "cancel",
            "cancellation",
        )):
            return CUSTOMER_HELP["cancel"]

        if any(term in q for term in (
            "feedback",
            "give a rating",
            "submit a rating",
            "rate the technician",
            "review the service",
        )):
            return CUSTOMER_HELP["feedback"]

        if any(term in q for term in (
            "track my",
            "track a service",
            "track request",
            "where is my request",
            "check my request status",
            "how do i track",
            "how to track",
        )):
            return CUSTOMER_HELP["track"]

        if any(term in q for term in (
            "how do i view history",
            "how to view history",
            "how do i see history",
            "where can i find history",
            "how to check history",
            "how do i view my history",
        )):
            return CUSTOMER_HELP["history"]

        if any(term in q for term in (
            "how do i use the customer portal",
            "help me use the customer portal",
            "customer portal help",
            "how does the portal work",
        )):
            return CUSTOMER_HELP["default"]

    elif role == "technician":
        if any(term in q for term in (
            "customer location",
            "customer address",
            "where is the customer",
            "find the customer",
            "customer details",
            "customer contact",
        )):
            return TECHNICIAN_HELP["location"]

        if any(term in q for term in (
            "update status",
            "change status",
            "mark as completed",
            "mark job complete",
            "how do i complete a job",
            "how to update a job",
            "how do i update a job",
        )):
            return TECHNICIAN_HELP["status"]

        if any(term in q for term in (
            "how do i view assigned jobs",
            "how to view assigned jobs",
            "where are my assigned jobs",
            "how do i see assigned jobs",
            "how do i view my jobs",
            "how to view my jobs",
        )):
            return TECHNICIAN_HELP["jobs"]

        if any(term in q for term in (
            "how do i view completed jobs",
            "how to view completed jobs",
            "where are my completed jobs",
            "how do i see completed jobs",
        )):
            return TECHNICIAN_HELP["completed"]

        if any(term in q for term in (
            "how do i use the technician portal",
            "technician portal help",
            "help me use the technician portal",
        )):
            return TECHNICIAN_HELP["default"]

    return None


def _format_help_response(question, answer):
    return {
        "question": question,
        "sql": "",
        "result_count": 0,
        "results": [],
        "answer": answer,
    }


# ============================================================
# DATABASE QUESTION CLASSIFICATION
# ============================================================

def _get_user_record_id(session, role, user_uuid):
    """Resolve the authenticated UUID to the internal database ID."""
    if role == "customer":
        query = text("""
            SELECT customer_id
            FROM customers
            WHERE customer_uuid = :user_uuid
        """)
    elif role == "technician":
        query = text("""
            SELECT technician_id
            FROM technicians
            WHERE technician_uuid = :user_uuid
        """)
    else:
        raise ValueError("Unsupported user role.")

    result = session.exec(
        query,
        params={"user_uuid": str(user_uuid)},
    ).first()

    return result[0] if result else None


def _get_question_type(question):
    """Classify supported database questions."""
    q = _normalize_question(question)

    if (
        any(term in q for term in (
            "highest rating",
            "highest rated",
            "top rated",
            "best rated",
            "technician with the highest",
        ))
        or (
            "technician" in q
            and "rating" in q
            and any(word in q for word in (
                "who", "which", "best", "top", "highest"
            ))
        )
    ):
        return "highest_rated_technician"

    if (
        "technician" in q
        and any(term in q for term in (
            "how many",
            "number of",
            "count",
            "total",
            "registered",
            "available",
        ))
    ):
        return "technician_count"

    if (
        any(term in q for term in (
            "service",
            "services",
            "skill",
            "skills",
            "offering",
            "offerings",
        ))
        and any(term in q for term in (
            "available",
            "what are",
            "what is",
            "show",
            "list",
            "catalogue",
            "catalog",
            "offerings",
            "provide",
            "offered",
            "how many",
            "number of",
            "count",
            "total",
        ))
        and not any(term in q for term in (
            "request",
            "requests",
            "history",
            "completed",
            "pending",
            "assigned",
            "my service",
        ))
    ):
        if any(term in q for term in (
            "how many",
            "number of",
            "count",
            "total",
        )):
            return "service_count"

        return "service_catalogue"

    if any(term in q for term in (
        "history",
        "previous status",
        "status history",
        "past updates",
        "what changed",
        "changes made",
        "previous updates",
    )):
        return "history"

    if any(term in q for term in (
        "completed",
        "complete",
        "finished",
        "resolved",
    )):
        if any(term in q for term in (
            "how many",
            "count",
            "number of",
            "total",
        )):
            return "completed_count"

        return "completed"

    if any(term in q for term in (
        "pending",
        "not completed",
        "unfinished",
        "still open",
        "in progress",
        "ongoing",
    )):
        if any(term in q for term in (
            "how many",
            "count",
            "number of",
            "total",
        )):
            return "pending_count"

        return "pending"

    if (
        any(term in q for term in (
            "how many",
            "count",
            "number of",
            "total",
            "how much work",
        ))
        and any(term in q for term in (
            "request",
            "requests",
            "service request",
            "assignment",
            "assignments",
            "job",
            "jobs",
            "workload",
        ))
    ):
        return "count"

    if any(term in q for term in (
        "request",
        "requests",
        "assigned",
        "assignment",
        "assignments",
        "workload",
        "job",
        "jobs",
        "status",
        "show my",
        "list my",
        "what am i",
        "what is my",
        "my work",
    )):
        return "list"

    return None


# ============================================================
# HUMAN-READABLE DATABASE ANSWERS
# ============================================================

def _build_database_answer(question_type, results, role):
    """Build a readable answer from the predefined query results."""
    if question_type == "technician_count":
        count = results[0]["technician_count"] if results else 0
        return f"There are {count} registered technician(s) in the system."

    if question_type == "service_count":
        count = results[0]["service_count"] if results else 0
        return f"There are {count} service(s) available in the system."

    if question_type == "service_catalogue":
        if not results:
            return "No services were found in the service catalogue."

        names = [
            str(row["skill_name"])
            for row in results
            if row.get("skill_name")
        ]
        if names:
            return (
                f"I found {len(results)} service record(s): "
                + ", ".join(names)
                + "."
            )
        return f"I found {len(results)} service record(s)."

    if question_type == "highest_rated_technician":
        if not results:
            return "No rated technicians were found."

        rating = results[0].get("rating")
        names = [
            str(row["technician_name"])
            for row in results
            if row.get("technician_name")
        ]

        if len(names) == 1:
            return f"{names[0]} has the highest technician rating: {rating}/5."

        return (
            f"{', '.join(names)} share the highest technician rating: "
            f"{rating}/5."
        )

    if question_type in (
        "count",
        "completed_count",
        "pending_count",
    ):
        count = results[0]["request_count"] if results else 0

        if question_type == "completed_count":
            return f"You have {count} completed service request(s)."

        if question_type == "pending_count":
            return f"You have {count} pending or in-progress service request(s)."

        noun = "service request(s)" if role == "customer" else "assigned request(s)"
        return f"You have {count} matching {noun}."

    if question_type == "history":
        if not results:
            return "No service history records were found for your requests."
        return f"I found {len(results)} service history record(s) for your requests."

    if question_type == "completed":
        if not results:
            return "You have no completed service requests in the available records."
        return f"I found {len(results)} completed service request(s)."

    if question_type == "pending":
        if not results:
            return "You have no pending or in-progress service requests in the available records."
        return f"I found {len(results)} pending or in-progress service request(s)."

    if question_type == "list":
        if not results:
            return "No matching service requests were found."
        return f"I found {len(results)} service request(s) associated with your account."

    return "The query completed successfully."


# ============================================================
# MAIN AI SERVICE
# ============================================================

def answer_ai_question(question, user_uuid, role):
    """
    Answer supported procedural and database questions.

    Procedural guidance does not open a database session.
    Database questions use predefined, read-only SQL queries.
    Personal request data is restricted to the authenticated user.
    """
    question = question.strip()
    role = str(role).lower()

    if not question:
        raise ValueError("Question cannot be empty.")

    if role not in {"customer", "technician"}:
        raise PermissionError(
            "This role cannot use the AI Assistant."
        )

    help_answer = _get_help_response(question, role)
    if help_answer is not None:
        return _format_help_response(question, help_answer)

    question_type = _get_question_type(question)

    if question_type is None:
        raise ValueError(
            "Try asking about booking, tracking, cancellation guidance, "
            "feedback, technician counts, available services, technician "
            "ratings, your service requests, completed or pending work, "
            "or service history."
        )

    with get_session_context() as session:
        session.exec(text("SET TRANSACTION READ ONLY"))
        session.exec(text("SET LOCAL statement_timeout = '5s'"))

        user_record_id = _get_user_record_id(
            session,
            role,
            user_uuid,
        )

        if user_record_id is None:
            raise PermissionError(
                "User account could not be verified."
            )

        params = {}

        if question_type == "technician_count":
            sql = """
                SELECT COUNT(*) AS technician_count
                FROM technicians
            """

        elif question_type == "service_count":
            sql = """
                SELECT COUNT(*) AS service_count
                FROM skills
            """

        elif question_type == "service_catalogue":
            sql = """
                SELECT
                    skill_name,
                    category,
                    description,
                    estimated_duration
                FROM skills
                ORDER BY skill_name
                LIMIT 100
            """

        elif question_type == "highest_rated_technician":
            sql = """
                SELECT
                    technician_name,
                    rating
                FROM technicians
                WHERE rating IS NOT NULL
                  AND rating > 0
                  AND rating = (
                      SELECT MAX(rating)
                      FROM technicians
                      WHERE rating IS NOT NULL
                        AND rating > 0
                  )
                ORDER BY technician_name
                LIMIT 100
            """

        else:
            if role == "customer":
                params["customer_id"] = user_record_id
                base_condition = "sr.customer_id = :customer_id"
            else:
                params["technician_id"] = user_record_id
                base_condition = """
                    (
                        sr.assigned_technician_id = :technician_id
                        OR EXISTS (
                            SELECT 1
                            FROM assignments a
                            WHERE a.request_id = sr.request_id
                              AND a.technician_id = :technician_id
                        )
                    )
                """

            if question_type in (
                "count",
                "completed_count",
                "pending_count",
            ):
                sql = f"""
                    SELECT COUNT(*) AS request_count
                    FROM service_requests sr
                    WHERE {base_condition}
                """

                if question_type == "completed_count":
                    sql += " AND UPPER(sr.status) = 'COMPLETED'"
                elif question_type == "pending_count":
                    sql += """
                        AND UPPER(sr.status) IN (
                            'PENDING',
                            'IN_PROGRESS',
                            'IN PROGRESS'
                        )
                    """

            elif question_type == "history":
                sql = f"""
                    SELECT
                        sh.old_status,
                        sh.new_status,
                        sh.updated_time,
                        sh.remarks
                    FROM service_history sh
                    JOIN service_requests sr
                      ON sr.request_id = sh.request_id
                    WHERE {base_condition}
                    ORDER BY sh.updated_time DESC
                    LIMIT {MAX_RESULTS}
                """

            else:
                sql = f"""
                    SELECT
                        sr.request_uuid,
                        sr.problem_description,
                        sr.priority,
                        sr.status,
                        sr.request_date
                    FROM service_requests sr
                    WHERE {base_condition}
                """

                if question_type == "completed":
                    sql += " AND UPPER(sr.status) = 'COMPLETED'"
                elif question_type == "pending":
                    sql += """
                        AND UPPER(sr.status) IN (
                            'PENDING',
                            'IN_PROGRESS',
                            'IN PROGRESS'
                        )
                    """

                sql += f"""
                    ORDER BY sr.request_date DESC
                    LIMIT {MAX_RESULTS}
                """

        result = session.exec(text(sql), params=params)
        rows = result.fetchmany(MAX_RESULTS)
        results = [dict(row._mapping) for row in rows]

        answer = _build_database_answer(
            question_type,
            results,
            role,
        )

        return {
            "question": question,
            "sql": sql,
            "result_count": len(results),
            "results": results,
            "answer": answer,
        }
