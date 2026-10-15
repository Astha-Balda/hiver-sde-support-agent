"""Download assets during the build, before the 512 MiB runtime starts."""

from dotenv import load_dotenv

from src.embeddings import get_model_files
from src.retriever import get_asset


def main():
    load_dotenv()
    get_asset("SUPPORT_INDEX_FILE", "support_pairs.index", local_files_only=False)
    get_asset("SUPPORT_METADATA_FILE", "support_pairs_metadata.json", local_files_only=False)
    get_model_files(local_files_only=False)
    print("Support data and quantized ONNX model cached for runtime.", flush=True)


if __name__ == "__main__":
    main()
