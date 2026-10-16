import chromadb
import re

from sqlmodel import select

from Orm.database import get_session_context
from Orm.skills import Skill


CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "service_skills"

# Maximum distance allowed for a semantic match.
# Lower distance means better similarity.
SEMANTIC_DISTANCE_THRESHOLD = 1.0


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def normalize_text(text):

    text = str(text).lower()

    text = text.replace("-", " ")
    text = text.replace("/", " ")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


SERVICE_ALIASES = {

    "ac repair": [
        "ac",
        "a c",
        "air conditioner",
        "air conditioning",
        "air conditioner repair",
        "ac service",
        "ac not cooling",
        "ac cooling problem"
    ],

    "air cooler repair": [
        "air cooler",
        "cooler",
        "desert cooler",
        "room cooler",
        "cooler repair"
    ],

    "washing machine repair": [
        "washing machine",
        "washing machines",
        "washer",
        "washing machine repair"
    ],

    "refrigerator repair": [
        "refrigerator",
        "fridge",
        "refrigerator repair",
        "fridge repair"
    ],

    "tv repair": [
        "tv",
        "television",
        "smart tv",
        "tv repair"
    ],

    "plumbing": [
        "plumbing",
        "pipe",
        "water leakage",
        "water leak",
        "tap",
        "faucet",
        "sink",
        "drain",
        "pipe leakage"
    ]
}


def add_service_to_chroma(
    skill_id,
    skill_name,
    category,
    description
):

    document = (
        f"Service: {skill_name}. "
        f"Category: {category}. "
        f"Description: {description}"
    )

    collection.upsert(

        ids=[
            str(skill_id)
        ],

        documents=[
            document
        ],

        metadatas=[
            {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "category": category
            }
        ]
    )


def find_keyword_service(
    problem_description
):

    problem = normalize_text(
        problem_description
    )

    results = collection.get(
        include=[
            "metadatas",
            "documents"
        ]
    )

    if not results["ids"]:

        return None

    best_match = None
    best_score = 0

    for index in range(
        len(results["ids"])
    ):

        metadata = results["metadatas"][index]

        document = results["documents"][index]

        skill_name = normalize_text(
            metadata["skill_name"]
        )

        score = 0

        if skill_name in problem:

            score += 100

        service_words = skill_name.split()

        for word in service_words:

            if len(word) >= 3 and word in problem:

                score += 20

        for service_key, aliases in SERVICE_ALIASES.items():

            if skill_name == service_key:

                for alias in aliases:

                    alias = normalize_text(alias)

                    if alias in problem:

                        score += (
                            80
                            + len(alias.split()) * 10
                        )

        if score > best_score:

            best_score = score

            best_match = {

                "skill_id": int(
                    metadata["skill_id"]
                ),

                "skill_name": metadata[
                    "skill_name"
                ],

                "category": metadata[
                    "category"
                ],

                "document": document,

                "score": best_score,

                "match_type": "Keyword Match"
            }

    return best_match


def find_semantic_service(
    problem_description
):

    results = collection.query(

        query_texts=[
            problem_description
        ],

        n_results=1
    )

    if not results["ids"]:

        return None

    if not results["ids"][0]:

        return None

    skill_id = results["ids"][0][0]

    document = results["documents"][0][0]

    metadata = results["metadatas"][0][0]

    distance = results["distances"][0][0]

    # ========================================================
    # CHECK SEMANTIC MATCH QUALITY
    # ========================================================

    if distance > SEMANTIC_DISTANCE_THRESHOLD:

        return None

    return {

        "skill_id": int(skill_id),

        "skill_name": metadata[
            "skill_name"
        ],

        "category": metadata[
            "category"
        ],

        "document": document,

        "distance": distance,

        "match_type": "Semantic Match"
    }


def find_service_by_problem(
    problem_description
):

    keyword_result = find_keyword_service(
        problem_description
    )

    if keyword_result:

        return keyword_result

    semantic_result = find_semantic_service(
        problem_description
    )

    if semantic_result:

        return semantic_result

    return None


def refresh_service_collection():

    with get_session_context() as session:

        skills = session.exec(
            select(Skill)
        ).all()

    if not skills:

        print(
            "No skills found in PostgreSQL."
        )

        return

    existing_ids = collection.get()["ids"]

    if existing_ids:

        collection.delete(
            ids=existing_ids
        )

    for skill in skills:

        add_service_to_chroma(
            skill_id=skill.skill_id,
            skill_name=skill.skill_name,
            category=skill.category,
            description=skill.description
        )

    print(
        f"Service Chroma collection refreshed "
        f"with {len(skills)} skills."
    )