import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

input_file = "data/processed/amazonhelp_support_pairs.jsonl"

index_file = "data/processed/support_pairs.index"

metadata_file = "data/processed/support_pairs_metadata.json"


# --------------------------------------------------
# 2. Load support pairs
# --------------------------------------------------

print("Loading support pairs...")

queries = []
metadata = []

with open(input_file, "r", encoding="utf-8") as file:

    for line in file:

        if not line.strip():
            continue

        pair = json.loads(line)

        queries.append(pair["query"])

        metadata.append({
            "conversation_id": pair["conversation_id"],
            "query": pair["query"],
            "response": pair["response"]
        })


print("Support pairs loaded:", len(queries))


# --------------------------------------------------
# 3. Load embedding model
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# --------------------------------------------------
# 4. Generate embeddings
# --------------------------------------------------

print("\nGenerating embeddings...")

embeddings = model.encode(
    queries,
    show_progress_bar=True,
    batch_size=32,
    normalize_embeddings=True
)

embeddings = np.asarray(embeddings, dtype="float32")

print("Embedding shape:", embeddings.shape)


# --------------------------------------------------
# 5. Create FAISS index
# --------------------------------------------------

print("\nBuilding FAISS index...")

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)


print("Vectors added to index:", index.ntotal)


# --------------------------------------------------
# 6. Save index
# --------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

faiss.write_index(index, index_file)

with open(metadata_file, "w", encoding="utf-8") as file:

    json.dump(
        metadata,
        file,
        ensure_ascii=False,
        indent=2
    )


# --------------------------------------------------
# 7. Results
# --------------------------------------------------

print("\n" + "=" * 60)
print("VECTOR INDEX CREATED")
print("=" * 60)

print("Vectors:", index.ntotal)
print("Dimensions:", dimension)

print("\nSaved FAISS index:")
print(index_file)

print("\nSaved metadata:")
print(metadata_file)

print("\nVector indexing complete!")