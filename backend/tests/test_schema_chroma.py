from  unittest.mock import patch


from modules.schema_chroma import (
    extract_table_documents,
    extract_relationship_document,
    load_schema_to_chroma,
    identify_tables_from_question,
    requires_multiple_tables,
    search_schema,
)


# ============================================================
# EXTRACT TABLE DOCUMENTS
# ============================================================

@patch(
    "modules.schema_chroma.DATABASE_SCHEMA",
    """
TABLE: customers
Customer schema

TABLE: technicians
Technician schema

TABLE: skills
Skills schema

TABLE: technician_skills
Technician skills schema

TABLE: service_requests
Service request schema

TABLE: assignments
Assignment schema

TABLE: service_history
Service history schema

TABLE: feedback
Feedback schema

RELATIONSHIPS:
customers -> service_requests
"""
)
def test_extract_table_documents():

    result = extract_table_documents()

    assert len(result) == 8

    assert "customers" in result
    assert "technicians" in result
    assert "skills" in result
    assert "technician_skills" in result
    assert "service_requests" in result
    assert "assignments" in result
    assert "service_history" in result
    assert "feedback" in result

    assert "Business terminology:" in result["customers"]
    assert "Business terminology:" in result["technicians"]
    assert "Business terminology:" in result["skills"]
    assert "Business terminology:" in result["technician_skills"]
    assert "Business terminology:" in result["service_requests"]
    assert "Business terminology:" in result["assignments"]
    assert "Business terminology:" in result["service_history"]
    assert "Business terminology:" in result["feedback"]


# ============================================================
# EXTRACT TABLE DOCUMENTS - MISSING TABLES
# ============================================================

@patch(
    "modules.schema_chroma.DATABASE_SCHEMA",
    """
TABLE: customers
Customer schema

TABLE: technicians
Technician schema

RELATIONSHIPS:
customers -> technicians
"""
)
def test_extract_table_documents_missing_tables():

    result = extract_table_documents()

    assert "customers" in result
    assert "technicians" in result

    assert "skills" not in result
    assert "feedback" not in result


# ============================================================
# EXTRACT RELATIONSHIP DOCUMENT - SUCCESS
# ============================================================

@patch(
    "modules.schema_chroma.DATABASE_SCHEMA",
    """
TABLE: customers
Customer schema

RELATIONSHIPS:
customers -> service_requests
technicians -> service_requests
"""
)
def test_extract_relationship_document_success():

    result = extract_relationship_document()

    assert result.startswith(
        "DATABASE RELATIONSHIPS"
    )

    assert "customers -> service_requests" in result
    assert "technicians -> service_requests" in result


# ============================================================
# EXTRACT RELATIONSHIP DOCUMENT - NOT FOUND
# ============================================================

@patch(
    "modules.schema_chroma.DATABASE_SCHEMA",
    """
TABLE: customers
Customer schema
"""
)
def test_extract_relationship_document_not_found():

    result = extract_relationship_document()

    assert result == ""


# ============================================================
# LOAD SCHEMA - ALL DOCUMENTS
# ============================================================

@patch("modules.schema_chroma.schema_collection")
@patch("modules.schema_chroma.extract_relationship_document")
@patch("modules.schema_chroma.extract_table_documents")
def test_load_schema_to_chroma_success(
    mock_extract_tables,
    mock_extract_relationships,
    mock_collection
):

    mock_extract_tables.return_value = {
        "customers": "Customers schema",
        "technicians": "Technicians schema",
        "skills": "Skills schema",
        "technician_skills": "Technician skills schema",
        "service_requests": "Service requests schema",
        "assignments": "Assignments schema",
        "service_history": "Service history schema",
        "feedback": "Feedback schema",
    }

    mock_extract_relationships.return_value = (
        "DATABASE RELATIONSHIPS\n"
        "customers -> service_requests"
    )

    with patch("builtins.print") as mock_print:

        load_schema_to_chroma()

    mock_collection.upsert.assert_called_once()

    call_kwargs = (
        mock_collection.upsert.call_args.kwargs
    )

    assert len(call_kwargs["ids"]) == 9

    assert "customers" in call_kwargs["ids"]
    assert "technicians" in call_kwargs["ids"]
    assert "skills" in call_kwargs["ids"]
    assert "technician_skills" in call_kwargs["ids"]
    assert "service_requests" in call_kwargs["ids"]
    assert "assignments" in call_kwargs["ids"]
    assert "service_history" in call_kwargs["ids"]
    assert "feedback" in call_kwargs["ids"]
    assert "relationships" in call_kwargs["ids"]

    assert call_kwargs["metadatas"][-1] == {
        "type": "relationships",
        "table": "relationships"
    }

    mock_print.assert_called_once_with(
        "\n9 schema documents "
        "loaded into ChromaDB successfully."
    )


# ============================================================
# LOAD SCHEMA - MISSING TABLES / NO RELATIONSHIPS
# ============================================================

@patch("modules.schema_chroma.schema_collection")
@patch("modules.schema_chroma.extract_relationship_document")
@patch("modules.schema_chroma.extract_table_documents")
def test_load_schema_to_chroma_missing_documents(
    mock_extract_tables,
    mock_extract_relationships,
    mock_collection
):

    mock_extract_tables.return_value = {
        "customers": "Customers schema",
        "technicians": "",
        "skills": None,
    }

    mock_extract_relationships.return_value = ""

    with patch("builtins.print") as mock_print:

        load_schema_to_chroma()

    mock_collection.upsert.assert_called_once()

    call_kwargs = (
        mock_collection.upsert.call_args.kwargs
    )

    assert call_kwargs["ids"] == [
        "customers"
    ]

    assert call_kwargs["documents"] == [
        "Customers schema"
    ]

    assert call_kwargs["metadatas"] == [
        {
            "type": "table_schema",
            "table": "customers"
        }
    ]

    mock_print.assert_called_once_with(
        "\n1 schema documents "
        "loaded into ChromaDB successfully."
    )


# ============================================================
# IDENTIFY TABLES - BUSINESS TERMS
# ============================================================

def test_identify_tables_from_question():

    result = identify_tables_from_question(
        """
        Show customer and technician information
        with service requests, technician skills,
        assignments, service history, feedback,
        ratings and services.
        """
    )

    assert "customers" in result
    assert "technicians" in result
    assert "skills" in result
    assert "service_requests" in result
    assert "technician_skills" in result
    assert "assignments" in result
    assert "service_history" in result
    assert "feedback" in result

    assert len(result) == 8


# ============================================================
# IDENTIFY TABLES - DUPLICATES
# ============================================================

def test_identify_tables_duplicates_removed():

    result = identify_tables_from_question(
        "Show customers and customer clients"
    )

    assert result == [
        "customers"
    ]


# ============================================================
# IDENTIFY TABLES - NO MATCH
# ============================================================

def test_identify_tables_no_match():

    result = identify_tables_from_question(
        "What is the weather today?"
    )

    assert result == []


# ============================================================
# IDENTIFY TABLES - LONGER PHRASES
# ============================================================

def test_identify_tables_longer_phrases():

    result = identify_tables_from_question(
        "Show service requests and technician skills"
    )

    assert result == [
        "service_requests",
        "technician_skills",
        "technicians",
        "skills",
    ]


# ============================================================
# REQUIRES MULTIPLE TABLES - TRUE
# ============================================================

def test_requires_multiple_tables_true():

    questions = [
        "Show customer name and technician name",
        "Show customer name and service name",
        "Show technician name and service name",
        "Show customer and technician",
        "Show technician and service",
        "Show customer and service",
        "Who provides plumbing?",
        "Who can provide AC repair?",
        "Show services provided by technicians",
        "Show assigned technician",
        "Show technician for each request",
        "Show service for each request",
        "Show customers for each service",
        "Show customer along with technician",
        "Show customer together with technician",
    ]

    for question in questions:

        assert requires_multiple_tables(
            question
        ) is True


# ============================================================
# REQUIRES MULTIPLE TABLES - FALSE
# ============================================================

def test_requires_multiple_tables_false():

    assert requires_multiple_tables(
        "Show all customers"
    ) is False


# ============================================================
# SEARCH SCHEMA - NO DOCUMENTS
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_no_documents(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": []
    }

    result = search_schema(
        "Show customers"
    )

    assert result == []


# ============================================================
# SEARCH SCHEMA - EMPTY FIRST DOCUMENT LIST
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_empty_first_document_list(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            []
        ]
    }

    result = search_schema(
        "Show customers"
    )

    assert result == []


# ============================================================
# SEARCH SCHEMA - DISTANCE TOO HIGH
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_distance_too_high(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Customers schema"
            ]
        ],
        "distances": [
            [
                2.0
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "customers"
                }
            ]
        ]
    }

    with patch("builtins.print"):

        result = search_schema(
            "Show customers"
        )

    assert result == []


# ============================================================
# SEARCH SCHEMA - SIMPLE EXPLICIT TABLE
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_simple_explicit_table(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Customers schema"
            ]
        ],
        "distances": [
            [
                0.25
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "customers"
                }
            ]
        ]
    }

    mock_collection.get.return_value = {
        "documents": [
            "Customers schema"
        ]
    }

    with patch("builtins.print"):

        result = search_schema(
            "Show customers"
        )

    assert result == [
        "Customers schema"
    ]

    mock_collection.get.assert_called_once_with(
        ids=[
            "customers"
        ],
        include=[
            "documents",
            "metadatas"
        ]
    )


# ============================================================
# SEARCH SCHEMA - NO EXPLICIT TABLE
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_no_explicit_table(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Customers schema"
            ]
        ],
        "distances": [
            [
                0.20
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "customers"
                }
            ]
        ]
    }

    mock_collection.get.return_value = {
        "documents": [
            "Customers schema"
        ]
    }

    with patch(
        "modules.schema_chroma.identify_tables_from_question"
    ) as mock_identify:

        mock_identify.return_value = []

        with patch("builtins.print"):

            result = search_schema(
                "Show some database information"
            )

    assert result == [
        "Customers schema"
    ]


# ============================================================
# SEARCH SCHEMA - INVALID MAIN TABLE
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_invalid_main_table(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Unknown schema"
            ]
        ],
        "distances": [
            [
                0.20
            ]
        ],
        "metadatas": [
            [
                {}
            ]
        ]
    }

    with patch(
        "modules.schema_chroma.identify_tables_from_question"
    ) as mock_identify:

        mock_identify.return_value = []

        with patch("builtins.print"):

            result = search_schema(
                "Show unknown information"
            )

    assert result == []


# ============================================================
# SEARCH SCHEMA - RELATED DOCUMENTS MISSING
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_related_documents_missing(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Customers schema"
            ]
        ],
        "distances": [
            [
                0.20
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "customers"
                }
            ]
        ]
    }

    mock_collection.get.return_value = {
        "documents": []
    }

    with patch("builtins.print"):

        result = search_schema(
            "Show customers"
        )

    assert result == []


# ============================================================
# SEARCH SCHEMA - COMPLEX QUESTION
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_complex_question(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Service request schema"
            ]
        ],
        "distances": [
            [
                0.30
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "service_requests"
                }
            ]
        ]
    }

    mock_collection.get.side_effect = [
        {
            "documents": [
                "Service request schema",
                "Customer schema",
                "Technician schema"
            ]
        },
        {
            "documents": [
                "Relationship schema"
            ]
        }
    ]

    with patch("builtins.print"):

        result = search_schema(
            "Show customer name and technician name "
            "for each request"
        )

    assert result == [
        "Service request schema",
        "Customer schema",
        "Technician schema",
        "Relationship schema"
    ]

    assert mock_collection.get.call_count == 2


# ============================================================
# SEARCH SCHEMA - COMPLEX WITHOUT RELATIONSHIPS
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_complex_without_relationships(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Service request schema"
            ]
        ],
        "distances": [
            [
                0.30
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "service_requests"
                }
            ]
        ]
    }

    mock_collection.get.side_effect = [
        {
            "documents": [
                "Service request schema",
                "Customer schema"
            ]
        },
        {
            "documents": []
        }
    ]

    with patch("builtins.print"):

        result = search_schema(
            "Show customer name and technician name "
            "for each request"
        )

    assert result == [
        "Service request schema",
        "Customer schema"
    ]


# ============================================================
# SEARCH SCHEMA - DUPLICATE DOCUMENTS
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_duplicate_documents(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Customers schema"
            ]
        ],
        "distances": [
            [
                0.25
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "customers"
                }
            ]
        ]
    }

    mock_collection.get.return_value = {
        "documents": [
            "Customers schema",
            "Customers schema",
            "Customers schema"
        ]
    }

    with patch("builtins.print"):

        result = search_schema(
            "Show customers"
        )

    assert result == [
        "Customers schema"
    ]


# ============================================================
# SEARCH SCHEMA - UNKNOWN RELATED TABLE FALLBACK
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_related_table_fallback(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Unknown table schema"
            ]
        ],
        "distances": [
            [
                0.20
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "unknown_table"
                }
            ]
        ]
    }

    mock_collection.get.side_effect = [
        {
            "documents": [
                "Unknown table schema"
            ]
        },
        {
            "documents": []
        }
    ]

    with patch(
        "modules.schema_chroma.identify_tables_from_question"
    ) as mock_identify:

        mock_identify.return_value = [
            "unknown_table"
        ]

        with patch(
            "modules.schema_chroma.requires_multiple_tables"
        ) as mock_requires_multiple:

            mock_requires_multiple.return_value = True

            with patch("builtins.print"):

                result = search_schema(
                    "Show unknown table and technician"
                )

    assert result == [
        "Unknown table schema"
    ]

    assert mock_collection.get.call_count == 2

    assert mock_collection.get.call_args_list[0].kwargs == {
        "ids": [
            "unknown_table"
        ],
        "include": [
            "documents",
            "metadatas"
        ]
    }

    assert mock_collection.get.call_args_list[1].kwargs == {
        "ids": [
            "relationships"
        ],
        "include": [
            "documents"
        ]
    }


# ============================================================
# SEARCH SCHEMA - RELATED TABLES NORMAL PATH
# ============================================================

@patch("modules.schema_chroma.schema_collection")
def test_search_schema_related_tables_normal_path(
    mock_collection
):

    mock_collection.query.return_value = {
        "documents": [
            [
                "Service request schema"
            ]
        ],
        "distances": [
            [
                0.20
            ]
        ],
        "metadatas": [
            [
                {
                    "table": "service_requests"
                }
            ]
        ]
    }

    mock_collection.get.side_effect = [
        {
            "documents": [
                "Service request schema",
                "Customer schema",
                "Technician schema",
                "Skills schema",
                "Relationships schema"
            ]
        },
        {
            "documents": [
                "Relationships schema"
            ]
        }
    ]

    with patch(
        "modules.schema_chroma.identify_tables_from_question"
    ) as mock_identify:

        mock_identify.return_value = [
            "service_requests"
        ]

        with patch(
            "modules.schema_chroma.requires_multiple_tables"
        ) as mock_requires_multiple:

            mock_requires_multiple.return_value = True

            with patch("builtins.print"):

                result = search_schema(
                    "Show customer name and technician name "
                    "for each service request"
                )

    assert result == [
        "Service request schema",
        "Customer schema",
        "Technician schema",
        "Skills schema",
        "Relationships schema"
    ]

    assert mock_collection.get.call_count == 2

    assert mock_collection.get.call_args_list[0].kwargs == {
        "ids": [
            "service_requests",
            "customers",
            "technicians",
            "skills",
            "relationships"
        ],
        "include": [
            "documents",
            "metadatas"
        ]
    }

    assert mock_collection.get.call_args_list[1].kwargs == {
        "ids": [
            "relationships"
        ],
        "include": [
            "documents"
        ]
    }

# ============================================================
# EXTRACT TABLE DOCUMENTS - UNKNOWN TABLE
# ============================================================

@patch(
    "modules.schema_chroma.TABLE_NAMES",
    [
        "unknown_table"
    ]
)
@patch(
    "modules.schema_chroma.DATABASE_SCHEMA",
    """
TABLE: unknown_table
Unknown table schema

RELATIONSHIPS:
unknown_table -> customers
"""
)
def test_extract_table_documents_unknown_table():

    result = extract_table_documents()

    assert result == {
        "unknown_table": (
            "TABLE: unknown_table\n"
            "Unknown table schema"
        )
    }