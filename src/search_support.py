import json
import faiss
from sentence_transformers import SentenceTransformer

index_file = "data/processed/support_pairs.index"
metadata_file = "data/processed/support_pairs_metadata.json"

print("Loading FAISS index...")
index = faiss.read_index(index_file)

print("Loading metadata...")
with open(metadata_file, "r", encoding="utf-8") as file:
    metadata = json.load(file)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def search_support(query, top_k=5):
    embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, indices = index.search(embedding, top_k)

    print("\n" + "=" * 70)
    print("CUSTOMER QUERY")
    print("=" * 70)
    print(query)

    print("\n" + "=" * 70)
    print("SIMILAR SUPPORT CASES")
    print("=" * 70)

    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        result = metadata[idx]

        print(f"\n--- Result {rank} ---")
        print("Similarity:", round(float(score), 4))
        print("Customer:", result["query"])
        print("Agent:", result["response"])


if __name__ == "__main__":
    query = input("\nEnter customer query: ")
    search_support(query)