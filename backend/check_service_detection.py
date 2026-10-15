from modules.chroma_service import (
    collection,
    find_keyword_service,
    find_semantic_service,
    find_service_by_problem,
)

problem = "my ac is running but not cooling"

print("\n--- COLLECTION ---")
print("Collection count:", collection.count())

print("\n--- KEYWORD MATCH ---")
print(find_keyword_service(problem))

print("\n--- SEMANTIC MATCH ---")
print(find_semantic_service(problem))

print("\n--- FINAL RESULT ---")
print(find_service_by_problem(problem))

print("\n--- STORED SERVICES ---")
results = collection.get(
    include=["metadatas", "documents"]
)

for metadata, document in zip(
    results["metadatas"],
    results["documents"],
):
    print(
        metadata.get("skill_id"),
        metadata.get("skill_name"),
        "|",
        document,
    )
