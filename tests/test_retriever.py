import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import faiss
import numpy as np

from src.retriever import DiskMetadata, SupportRetriever


class RetrievalTests(unittest.TestCase):
    def test_metadata_is_read_from_disk_in_original_index_order(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "metadata.json"
            source.write_text(json.dumps([
                {"query": "Refund", "response": "Refund information"},
                {"query": "Livraison", "response": "Votre colis est arrivé."},
            ]), encoding="utf-8")
            metadata = DiskMetadata(source)
            source.unlink()
            self.assertEqual(len(metadata), 2)
            self.assertEqual(metadata[1]["response"], "Votre colis est arrivé.")
            self.assertEqual(metadata[0]["query"], "Refund")
            with self.assertRaises(IndexError):
                metadata[2]

    def test_invalid_metadata_does_not_publish_a_partial_database(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "metadata.json"
            source.write_text('[{"query": "first"}, invalid]', encoding="utf-8")
            with self.assertRaises(ValueError):
                DiskMetadata(source)
            self.assertFalse(source.with_suffix(".sqlite3").exists())

    def test_search_preserves_cosine_ranking_and_skips_missing_neighbors(self):
        with tempfile.TemporaryDirectory() as directory:
            index_path = Path(directory) / "support.index"
            metadata_path = Path(directory) / "metadata.json"
            index = faiss.IndexFlatIP(2)
            index.add(np.array([[0, 1], [1, 0]], dtype=np.float32))
            faiss.write_index(index, str(index_path))
            metadata_path.write_text(json.dumps([
                {"query": "Order", "response": "Track the order"},
                {"query": "Refund", "response": "Check the refund"},
            ]), encoding="utf-8")
            with (
                patch.dict("os.environ", {
                    "SUPPORT_INDEX_FILE": str(index_path),
                    "SUPPORT_METADATA_FILE": str(metadata_path),
                }),
                patch("src.retriever.OnnxSentenceEncoder") as encoder,
            ):
                encoder.return_value.encode.return_value = np.array(
                    [[1, 0]], dtype=np.float32
                )
                retriever = SupportRetriever()
                results = retriever.search("Refund", top_k=3)
            self.assertEqual([row["query"] for row in results], ["Refund", "Order"])
            self.assertEqual([row["similarity"] for row in results], [1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
