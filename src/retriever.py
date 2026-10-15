import json
import os
import sqlite3
import tempfile
import threading
from contextlib import closing
from pathlib import Path

import faiss
import ijson
import numpy as np
from huggingface_hub import hf_hub_download

from src.embeddings import OnnxSentenceEncoder, get_cache_dir


class DiskMetadata:
    """Stream the JSON into SQLite instead of keeping every support case in RAM."""

    def __init__(self, source):
        source = Path(source).resolve()
        self.path = source.with_suffix(".sqlite3")
        with tempfile.NamedTemporaryFile(
            dir=source.parent, suffix=".sqlite3", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            with closing(sqlite3.connect(temporary_path)) as connection:
                connection.execute("PRAGMA cache_size = -2048")
                connection.execute("CREATE TABLE cases (id INTEGER PRIMARY KEY, payload TEXT)")
                with source.open("rb") as stream:
                    rows = (
                        (index, json.dumps(case, ensure_ascii=False))
                        for index, case in enumerate(ijson.items(stream, "item", use_float=True))
                    )
                    connection.executemany("INSERT INTO cases VALUES (?, ?)", rows)
                self.count = connection.execute("SELECT count(*) FROM cases").fetchone()[0]
                connection.commit()
            os.replace(temporary_path, self.path)
        except ijson.JSONError as exc:
            raise ValueError("Support metadata is not a valid JSON array") from exc
        finally:
            temporary_path.unlink(missing_ok=True)

    def __len__(self):
        return self.count

    def __getitem__(self, index):
        with closing(sqlite3.connect(f"{self.path.as_uri()}?mode=ro", uri=True)) as connection:
            row = connection.execute(
                "SELECT payload FROM cases WHERE id = ?", (int(index),)
            ).fetchone()
        if row is None:
            raise IndexError(index)
        return json.loads(row[0])


def get_asset(environment_name, filename, *, local_files_only=True):
    configured_path = os.getenv(environment_name)
    if configured_path and Path(configured_path).is_file():
        return configured_path
    repo_id = os.getenv("HF_DATASET_REPO")
    if not repo_id or repo_id.startswith("YOUR_USERNAME/"):
        raise ValueError("Set HF_DATASET_REPO to the Hugging Face dataset containing the support files")
    return hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type="dataset",
        token=os.getenv("HF_TOKEN"),
        cache_dir=get_cache_dir(),
        local_files_only=local_files_only,
    )


class SupportRetriever:
    def __init__(self):
        self._search_lock = threading.Lock()
        faiss.omp_set_num_threads(1)
        print("Loading support index and disk-backed metadata...", flush=True)
        index_path = get_asset("SUPPORT_INDEX_FILE", "support_pairs.index")
        metadata_path = get_asset("SUPPORT_METADATA_FILE", "support_pairs_metadata.json")
        self.index = faiss.read_index(str(index_path))
        self.metadata = DiskMetadata(metadata_path)
        if len(self.metadata) != self.index.ntotal:
            raise ValueError("Support metadata count does not match the FAISS index")
        print("Loading quantized ONNX embedding model...", flush=True)
        self.model = OnnxSentenceEncoder()
        print("Retriever ready (ONNX CPU, no PyTorch).", flush=True)

    def search(self, query, top_k=3):
        # Concurrent requests must not allocate several model activations at once.
        with self._search_lock:
            query_embedding = np.asarray(
                self.model.encode([query], normalize_embeddings=True), dtype="float32"
            )
            scores, indices = self.index.search(query_embedding, top_k)
            results = []
            for score, index in zip(scores[0], indices[0]):
                if index == -1:
                    continue
                result = self.metadata[index]
                result["similarity"] = float(score)
                results.append(result)
            return results


if __name__ == "__main__":
    retriever = SupportRetriever()
    for result in retriever.search("My package says delivered but I never received it."):
        print(result)
