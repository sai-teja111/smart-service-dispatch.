import re
import chromadb

from Ai.schema import DATABASE_SCHEMA


CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "database_schema"

MAX_DISTANCE = 1.55


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

schema_collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


TABLE_NAMES = [
    "customers",
    "technicians",
    "skills",
    "technician_skills",
    "service_requests",
    "assignments",
    "service_history",
    "feedback"
]


RELATED_TABLES = {

    "customers": [
        "customers"
    ],

    "technicians": [
        "technicians"
    ],

    "skills": [
        "skills"
    ],

    "technician_skills": [
        "technician_skills",
        "technicians",
        "skills",
        "relationships"
    ],

    "service_requests": [
        "service_requests",
        "customers",
        "technicians",
        "skills",
        "relationships"
    ],

    "assignments": [
        "assignments",
        "service_requests",
        "technicians",
        "relationships"
    ],

    "service_history": [
        "service_history",
        "service_requests",
        "relationships"
    ],

    "feedback": [
        "feedback",
        "customers",
        "technicians",
        "service_requests",
        "relationships"
    ]
}


# ============================================================
# BUSINESS TERM MAPPING
# ============================================================

BUSINESS_TERMS = {

    "customer": "customers",
    "customers": "customers",
    "client": "customers",
    "clients": "customers",

    "technician": "technicians",
    "technicians": "technicians",

    "service": "skills",
    "services": "skills",
    "skill": "skills",
    "skills": "skills",

    "service request": "service_requests",
    "service requests": "service_requests",
    "request": "service_requests",
    "requests": "service_requests",

    "technician skill": "technician_skills",
    "technician skills": "technician_skills",

    "assignment": "assignments",
    "assignments": "assignments",

    "service history": "service_history",
    "history": "service_history",

    "feedback": "feedback",

    "rating": "feedback",
    "ratings": "feedback"
}


# ============================================================
# EXTRACT TABLE DOCUMENTS FROM schema.py
# ============================================================

def extract_table_documents():

    documents = {}

    for table_name in TABLE_NAMES:

        pattern = (
            rf"(TABLE:\s+{re.escape(table_name)}"
            rf".*?)"
            rf"(?=\n\nTABLE:|\n\nRELATIONSHIPS:)"
        )

        match = re.search(
            pattern,
            DATABASE_SCHEMA,
            flags=re.IGNORECASE | re.DOTALL
        )

        if not match:

            continue

        document = match.group(1).strip()

        # ----------------------------------------------------
        # Add useful business terminology
        # ----------------------------------------------------

        if table_name == "customers":

            document += """

Business terminology:
customer
customers
client
clients
customer information
customer details
"""

        elif table_name == "technicians":

            document += """

Business terminology:
technician
technicians
available technician
available technicians
technician information
technician details
"""

        elif table_name == "skills":

            document += """

Business terminology:
service
services
company services
services provided
available services
skill
skills
"""

        elif table_name == "technician_skills":

            document += """

Business terminology:
technician skill
technician skills
expertise
experience
verified technician
verified skill
"""

        elif table_name == "service_requests":

            document += """

Business terminology:
service request
service requests
customer request
requests
open request
pending request
completed request
request status
request priority
"""

        elif table_name == "assignments":

            document += """

Business terminology:
assignment
assignments
assigned technician
technician assignment
assignment score
"""

        elif table_name == "service_history":

            document += """

Business terminology:
service history
history
status history
status changes
request history
"""

        elif table_name == "feedback":

            document += """

Business terminology:
feedback
customer feedback
comments
rating
ratings
feedback rating
"""

        documents[table_name] = document

    return documents


# ============================================================
# EXTRACT RELATIONSHIPS FROM schema.py
# ============================================================

def extract_relationship_document():

    match = re.search(
        r"RELATIONSHIPS:\s*(.*?)(?=\n\n#|$)",
        DATABASE_SCHEMA,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:

        return ""

    return (
        "DATABASE RELATIONSHIPS\n\n"
        + match.group(1).strip()
    )


# ============================================================
# LOAD SCHEMA INTO CHROMADB
# ============================================================

def load_schema_to_chroma():

    table_documents = (
        extract_table_documents()
    )

    relationship_document = (
        extract_relationship_document()
    )

    ids = []

    documents = []

    metadatas = []

    # ========================================================
    # LOAD TABLE DOCUMENTS
    # ========================================================

    for table_name in TABLE_NAMES:

        document = (
            table_documents.get(
                table_name
            )
        )

        if not document:

            continue

        ids.append(
            table_name
        )

        documents.append(
            document
        )

        metadatas.append(
            {
                "type": "table_schema",
                "table": table_name
            }
        )

    # ========================================================
    # LOAD RELATIONSHIPS
    # ========================================================

    if relationship_document:

        ids.append(
            "relationships"
        )

        documents.append(
            relationship_document
        )

        metadatas.append(
            {
                "type": "relationships",
                "table": "relationships"
            }
        )

    # ========================================================
    # UPSERT INTO CHROMADB
    # ========================================================

    schema_collection.upsert(

        ids=ids,

        documents=documents,

        metadatas=metadatas
    )

    print(
        f"\n{len(ids)} schema documents "
        "loaded into ChromaDB successfully."
    )


# ============================================================
# IDENTIFY EXPLICIT TABLES FROM QUESTION
# ============================================================

def identify_tables_from_question(question):

    question_lower = (
        question.lower().strip()
    )

    found_tables = []

    # --------------------------------------------------------
    # IMPORTANT:
    # Longer phrases must be checked first.
    # --------------------------------------------------------

    ordered_terms = [

        "service requests",
        "service request",

        "technician skills",
        "technician skill",

        "service history",

        "available technicians",
        "available technician",

        "verified technicians",
        "verified technician",

        "customers",
        "customer",
        "clients",
        "client",

        "technicians",
        "technician",

        "services",
        "service",

        "skills",
        "skill",

        "assignments",
        "assignment",

        "feedback",

        "ratings",
        "rating",

        "history",

        "requests",
        "request"
    ]

    for term in ordered_terms:

        if term not in question_lower:

            continue

        table = BUSINESS_TERMS.get(
            term
        )

        if table and table not in found_tables:

            found_tables.append(
                table
            )

    return found_tables


# ============================================================
# CHECK WHETHER QUESTION NEEDS MULTIPLE TABLES
# ============================================================

def requires_multiple_tables(question):

    question_lower = (
        question.lower()
    )

    indicators = [

        "for each",

        "along with",

        "together with",

        "customer name and technician name",

        "customer name and service name",

        "technician name and service name",

        "customer name, service name",

        "customer and technician",

        "technician and service",

        "customer and service",

        "who provides",

        "who can provide",

        "provided by",

        "assigned technician",

        "technician for each request",

        "service for each request"

    ]

    return any(
        indicator in question_lower
        for indicator in indicators
    )


# ============================================================
# SEARCH DATABASE SCHEMA
# ============================================================

def search_schema(question):

    # ========================================================
    # 1. IDENTIFY TABLES FROM BUSINESS TERMINOLOGY
    # ========================================================

    explicit_tables = (
        identify_tables_from_question(
            question
        )
    )

    # ========================================================
    # 2. SEARCH CHROMADB
    # ========================================================

    results = schema_collection.query(

        query_texts=[
            question
        ],

        n_results=5,

        include=[
            "documents",
            "distances",
            "metadatas"
        ]
    )

    # ========================================================
    # 3. CHECK RESULTS
    # ========================================================

    if not results.get("documents"):

        return []

    if not results["documents"][0]:

        return []

    documents = (
        results["documents"][0]
    )

    distances = (
        results["distances"][0]
    )

    metadatas = (
        results["metadatas"][0]
    )

    # ========================================================
    # 4. DISPLAY BEST CHROMA DISTANCE
    # ========================================================

    best_distance = distances[0]

    print(
        f"\nChromaDB similarity distance : "
        f"{best_distance:.4f}"
    )

    # ========================================================
    # 5. CHECK RELEVANCE
    # ========================================================

    if best_distance > MAX_DISTANCE:

        print(
            "\nChromaDB could not find a "
            "relevant database schema."
        )

        return []

    # ========================================================
    # 6. DETERMINE MAIN TABLE
    # ========================================================

    main_table = None

    if explicit_tables:

        main_table = (
            explicit_tables[0]
        )

    # ========================================================
    # 7. IF NO EXPLICIT TABLE,
    #    USE CHROMA'S BEST MATCH
    # ========================================================

    if not main_table:

        best_metadata = (
            metadatas[0]
        )

        main_table = (
            best_metadata.get(
                "table"
            )
        )

    # ========================================================
    # 8. INVALID MAIN TABLE
    # ========================================================

    if not main_table:

        print(
            "\nChromaDB could not identify "
            "a database table."
        )

        return []

    # ========================================================
    # 9. DISPLAY RETRIEVED MAIN TABLE
    # ========================================================

    print(
        f"\nChromaDB selected table : "
        f"{main_table}"
    )

    # ========================================================
    # 10. DETERMINE WHETHER JOIN IS REQUIRED
    # ========================================================

    join_required = (
        requires_multiple_tables(
            question
        )
    )

    # ========================================================
    # 11. SIMPLE QUESTION
    # ========================================================

    if not join_required:

        table_ids = [
            main_table
        ]

    # ========================================================
    # 12. COMPLEX QUESTION
    # ========================================================

    else:

        table_ids = (
            RELATED_TABLES.get(
                main_table,
                [
                    main_table
                ]
            )
        )

    # ========================================================
    # 13. GET SCHEMA DOCUMENTS
    # ========================================================

    related_results = (
        schema_collection.get(
            ids=table_ids,
            include=[
                "documents",
                "metadatas"
            ]
        )
    )

    if not related_results.get(
        "documents"
    ):

        return []

    # ========================================================
    # 14. DISPLAY RETRIEVED SCHEMAS
    # ========================================================

    print(
        "\n========== CHROMADB RETRIEVED SCHEMA =========="
    )

    for index, document in enumerate(

        related_results["documents"],

        start=1

    ):

        print(
            f"\n------------ RESULT {index} ------------"
        )

        print(
            document
        )

    print(
        "\n==============================================="
    )

    # ========================================================
    # 15. ADD RELATIONSHIPS FOR JOIN QUESTIONS
    # ========================================================

    final_documents = list(
        related_results["documents"]
    )

    if join_required:

        relationship_result = (
            schema_collection.get(
                ids=[
                    "relationships"
                ],
                include=[
                    "documents"
                ]
            )
        )

        if relationship_result.get(
            "documents"
        ):

            final_documents.extend(
                relationship_result["documents"]
            )

    # ========================================================
    # 16. REMOVE DUPLICATE DOCUMENTS
    # ========================================================

    unique_documents = []

    seen = set()

    for document in final_documents:

        cleaned = (
            document.strip()
        )

        if cleaned not in seen:

            unique_documents.append(
                cleaned
            )

            seen.add(
                cleaned
            )

    # ========================================================
    # 17. RETURN FINAL SCHEMA
    # ========================================================

    return unique_documents