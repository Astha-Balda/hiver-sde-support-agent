import json
import faiss
from sentence_transformers import SentenceTransformer

index_file = "data/processed/support_pairs.index"
metadata_file = "data/processed/support_pairs_metadata.json"

SIMILARITY_THRESHOLD = 0.75
TOP_K = 5


print("Loading FAISS index...")
index = faiss.read_index(index_file)

print("Loading metadata...")
with open(metadata_file, "r", encoding="utf-8") as file:
    metadata = json.load(file)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def search_support(query, top_k=TOP_K):
    embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, indices = index.search(embedding, top_k)

    best_score = float(scores[0][0])

    print("\n" + "=" * 70)
    print("CUSTOMER QUERY")
    print("=" * 70)
    print(query)

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULT")
    print("=" * 70)

    print("Best similarity score:", round(best_score, 4))
    print("Similarity threshold:", SIMILARITY_THRESHOLD)

    if best_score < SIMILARITY_THRESHOLD:
        print("\nStatus: LOW CONFIDENCE")
        print("No sufficiently relevant support case was found.")
        print("Recommended action: Ask for more information or escalate.")
        return

    print("\nStatus: RELEVANT CASES FOUND")

    print("\n" + "=" * 70)
    print("SIMILAR SUPPORT CASES")
    print("=" * 70)

    for rank, (score, idx) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):
        result = metadata[idx]

        print(f"\n--- Result {rank} ---")
        print("Similarity:", round(float(score), 4))
        print("Customer:", result["query"])
        print("Agent:", result["response"])


if __name__ == "__main__":
    query = input("\nEnter customer query: ").strip()

    if not query:
        print("Please enter a customer query.")
    else:
        search_support(query)