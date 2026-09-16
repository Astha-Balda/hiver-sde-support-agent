import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


INDEX_FILE = "data/processed/support_pairs.index"
METADATA_FILE = "data/processed/support_pairs_metadata.json"


class SupportRetriever:

    def __init__(self):
        print("Loading FAISS index...")
        self.index = faiss.read_index(INDEX_FILE)

        print("Loading metadata...")
        with open(METADATA_FILE, "r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Retriever ready.")

    def search(self, query, top_k=3):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            result = self.metadata[index].copy()
            result["similarity"] = float(score)

            results.append(result)

        return results


if __name__ == "__main__":

    retriever = SupportRetriever()

    query = "My package says delivered but I never received it."

    results = retriever.search(query, top_k=3)

    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("-" * 40)
        print("Similarity:", round(result["similarity"], 4))
        print("Query:", result["query"])
        print("Response:", result["response"])