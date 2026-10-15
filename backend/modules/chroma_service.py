
import re

import chromadb
from sqlmodel import select

from Orm.database import get_session_context
from Orm.skills import Skill


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "service_skills"
SEMANTIC_DISTANCE_THRESHOLD = 1.0
KEYWORD_MATCH_THRESHOLD = 65


client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    text = str(text or "").lower()
    text = re.sub(r"\ba\s*\.\s*c\.?\b", "ac", text)
    text = text.replace("-", " ").replace("/", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def contains_phrase(text, phrase):
    text = normalize_text(text)
    phrase = normalize_text(phrase)

    if not text or not phrase:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(phrase).replace(r"\ ", r"\s+")
        + r"(?![a-z0-9])"
    )
    return re.search(pattern, text) is not None


# ============================================================
# COMPACT ALIASES FOR ALL 20 SERVICES
# ============================================================

SERVICE_ALIASES = {
    "ac repair": [
        "ac", "air conditioner", "air conditioning",
        "not cooling", "gas refill", "compressor",
    ],
    "plumbing": [
        "plumber", "pipe leakage", "water leak", "tap",
        "faucet", "sink", "blocked drain", "drainage",
    ],
    "electrician": [
        "electrical wiring", "electrician", "short circuit",
        "switch repair", "socket", "circuit breaker", "fuse",
    ],
    "refrigerator repair": [
        "fridge", "refrigerator", "not cooling",
        "freezer", "compressor",
    ],
    "washing machine repair": [
        "washing machine", "washer", "not spinning",
        "not draining", "drum", "washing machine motor",
    ],
    "tv repair": [
        "tv", "television", "smart tv", "no picture",
        "no sound", "tv screen", "tv display",
    ],
    "ro water purifier service": [
        "ro purifier", "water purifier", "water filter",
        "ro membrane", "purifier installation",
    ],
    "microwave oven repair": [
        "microwave", "microwave oven", "not heating",
        "microwave sparks",
    ],
    "geyser repair": [
        "geyser", "water heater", "no hot water",
        "not heating", "thermostat",
    ],
    "air cooler repair": [
        "air cooler", "desert cooler", "room cooler",
        "cooler pump", "cooler motor",
    ],
    "laptop repair": [
        "laptop", "notebook computer", "laptop battery",
        "laptop keyboard", "laptop screen", "not charging",
    ],
    "mobile repair": [
        "mobile phone", "smartphone", "cell phone",
        "phone screen", "charging port", "mobile battery",
    ],
    "cctv installation": [
        "cctv", "security camera", "surveillance camera",
        "dvr", "nvr", "mobile viewing", "ip camera",
        "camera installation", "security surveillance",
        "remote camera viewing",
    ],
    "water tank cleaning": [
        "water tank cleaning", "overhead tank",
        "underground tank", "tank sanitation",
        "water storage tank",
    ],
    "house cleaning": [
        "house cleaning", "home cleaning", "deep cleaning",
        "apartment cleaning", "bathroom cleaning",
    ],
    "pest control": [
        "pest control", "cockroach", "termites",
        "bed bugs", "mosquito control", "rodents",
    ],
    "carpentry": [
        "carpenter", "woodwork", "door repair",
        "furniture repair", "cupboard", "wardrobe",
    ],
    "painting service": [
        "painting", "house painting", "wall painting",
        "repainting", "peeling paint", "wall cracks",
    ],
    "chimney repair": [
        "kitchen chimney", "chimney suction",
        "chimney motor", "chimney filter", "exhaust chimney",
    ],
    "water pump repair": [
        "water pump", "water motor", "borewell pump",
        "submersible pump", "not pumping water",
    ],
}


# ============================================================
# ADD ONE DOCUMENT PER SERVICE
# ============================================================

def add_service_to_chroma(
    skill_id,
    skill_name,
    category,
    description
):
    key = normalize_text(skill_name)
    aliases = SERVICE_ALIASES.get(key, [])

    document = (
        f"Service: {skill_name}. "
        f"Category: {category}. "
        f"Description: {description or ''}. "
        f"Related terms: {', '.join(aliases)}."
    )

    collection.upsert(
        ids=[str(skill_id)],
        documents=[document],
        metadatas=[{
            "skill_id": int(skill_id),
            "skill_name": skill_name,
            "category": category,
        }],
    )


# ============================================================
# KEYWORD MATCHING
# ============================================================

def find_keyword_service(problem_description):
    problem = normalize_text(problem_description)

    if not problem:
        return None

    results = collection.get(
        include=["metadatas", "documents"]
    )

    best_match = None
    best_score = 0
    tied = False

    for index, metadata in enumerate(results["metadatas"] or []):
        skill_name = metadata["skill_name"]
        key = normalize_text(skill_name)
        aliases = SERVICE_ALIASES.get(key, [])

        score = 0
        matched_phrases = []

        if contains_phrase(problem, key):
            score += 140
            matched_phrases.append(key)

        alias_scores = []

        for alias in aliases:
            if contains_phrase(problem, alias):
                normalized_alias = normalize_text(alias)
                word_count = len(normalized_alias.split())

                if word_count >= 3:
                    alias_score = 110
                elif word_count == 2:
                    alias_score = 90
                elif len(normalized_alias) >= 5:
                    alias_score = 80
                else:
                    alias_score = 68

                alias_scores.append((alias_score, normalized_alias))

        if alias_scores:
            alias_score, alias = max(alias_scores)
            score += alias_score
            matched_phrases.append(alias)

        if score > best_score:
            best_score = score
            tied = False
            best_match = {
                "skill_id": int(metadata["skill_id"]),
                "skill_name": skill_name,
                "category": metadata["category"],
                "document": results["documents"][index],
                "score": score,
                "matched_phrases": matched_phrases,
                "match_type": "Keyword Match",
            }
        elif score > 0 and score == best_score:
            tied = True

    if best_score < KEYWORD_MATCH_THRESHOLD or tied:
        return None

    return best_match


# ============================================================
# SEMANTIC MATCHING
# ============================================================

def find_semantic_service(problem_description):
    problem = str(problem_description or "").strip()

    if not problem or collection.count() == 0:
        return None

    results = collection.query(
        query_texts=[problem],
        n_results=min(3, collection.count()),
        include=["metadatas", "documents", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    if not ids:
        return None

    candidates = []

    for metadata, document, distance in zip(
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0],
    ):
        candidates.append({
            "skill_id": int(metadata["skill_id"]),
            "skill_name": metadata["skill_name"],
            "category": metadata["category"],
            "document": document,
            "distance": float(distance),
        })

    candidates.sort(key=lambda item: item["distance"])
    best = candidates[0]

    if best["distance"] > SEMANTIC_DISTANCE_THRESHOLD:
        return None

    # Avoid choosing between nearly identical semantic results.
    if (
        len(candidates) > 1
        and candidates[1]["distance"] <= SEMANTIC_DISTANCE_THRESHOLD
        and candidates[1]["distance"] - best["distance"] < 0.05
    ):
        return None

    best["match_type"] = "Semantic Match"
    return best


# ============================================================
# COMBINED DETECTION
# ============================================================

def find_service_by_problem(problem_description):
    problem = str(problem_description or "").strip()

    if not problem:
        return None

    keyword_result = find_keyword_service(problem)

    if keyword_result:
        return keyword_result

    return find_semantic_service(problem)


# ============================================================
# REFRESH FROM POSTGRESQL
# ============================================================

def refresh_service_collection():
    with get_session_context() as session:
        skills = session.exec(select(Skill)).all()

    if not skills:
        print("No skills found in PostgreSQL; collection unchanged.")
        return

    # Prepare database records before clearing the existing collection.
    service_data = [
        {
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "category": skill.category,
            "description": skill.description,
        }
        for skill in skills
    ]

    existing_ids = collection.get()["ids"]

    if existing_ids:
        collection.delete(ids=existing_ids)

    for skill in service_data:
        add_service_to_chroma(**skill)

    print(
        f"ChromaDB refreshed: {len(service_data)} services, "
        f"{collection.count()} documents."
    )
