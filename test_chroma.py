from modules.chroma_setup import load_services_to_chroma
from modules.chroma_service import find_service_by_problem


# ============================================================
# LOAD SERVICES
# ============================================================

print(
    "\nLoading services from  PostgreSQL into Chroma..."
)

load_services_to_chroma()


# ============================================================
# TEST CHROMA
# ============================================================

print("\n==========================================")
print("       CHROMA SERVICE DETECTION")
print("==========================================")


problem = input(
    "\nDescribe your problem: "
)


# ============================================================
# FIND SERVICE
# ============================================================

result = find_service_by_problem(
    problem
)


# ============================================================
# DISPLAY RESULT
# ============================================================

if result:

    print(
        "\n========== MATCHED SERVICE =========="
    )

    print(
        f"Skill ID : {result['skill_id']}"
    )

    print(
        f"Service  : {result['skill_name']}"
    )

    print(
        f"Category : {result['category']}"
    )

    print(
        f"Match    : {result['match_type']}"
    )

    # Distance exists only for semantic matching
    if "distance" in result:

        print(
            f"Distance : {result['distance']}"
        )

    # Score exists for keyword matching
    if "score" in result:

        print(
            f"Score    : {result['score']}"
        )

    print(
        f"Details  : {result['document']}"
    )

    print(
        "\nService detected successfully."
    )

else:

    print(
        "\nNo matching service found."
    )