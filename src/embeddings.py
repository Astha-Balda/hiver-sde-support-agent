"""CPU sentence embeddings without importing PyTorch or Transformers."""

import os
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer


MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "321b1453a093b6ed637ddb765600dbdd288610c8"


def get_cache_dir():
    # Resolve at use time so values loaded from .env are honored too.
    return Path(os.getenv(
        "SUPPORT_CACHE_DIR",
        str(Path(__file__).resolve().parents[1] / ".cache" / "huggingface"),
    ))


def get_model_files(*, local_files_only=True):
    return tuple(
        hf_hub_download(
            MODEL_REPO,
            filename,
            revision=MODEL_REVISION,
            cache_dir=get_cache_dir(),
            local_files_only=local_files_only,
        )
        for filename in ("tokenizer.json", "onnx/model_quint8_avx2.onnx")
    )


def mean_pool(token_embeddings, attention_mask):
    """Match MiniLM's attention-masked mean pooling and L2 normalization."""
    mask = attention_mask[..., None].astype(np.float32)
    pooled = (token_embeddings * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1e-9)
    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    return np.asarray(pooled / np.maximum(norms, 1e-9), dtype=np.float32)


class OnnxSentenceEncoder:
    def __init__(self):
        tokenizer_path, model_path = get_model_files()
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        # Match the original SentenceTransformer's sequence length.
        self.tokenizer.enable_truncation(max_length=256)
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False
        self.session = ort.InferenceSession(
            model_path, sess_options=options, providers=["CPUExecutionProvider"]
        )
        self.input_names = {item.name for item in self.session.get_inputs()}

    def encode(self, texts, normalize_embeddings=True):
        if not normalize_embeddings:
            raise ValueError("The support index requires normalized embeddings")
        # Process one sentence at a time to bound temporary activation memory.
        embeddings = []
        for text in texts:
            encoded = self.tokenizer.encode(text)
            inputs = {
                "input_ids": np.array([encoded.ids], dtype=np.int64),
                "attention_mask": np.array([encoded.attention_mask], dtype=np.int64),
                "token_type_ids": np.array([encoded.type_ids], dtype=np.int64),
            }
            output = self.session.run(
                None, {key: value for key, value in inputs.items() if key in self.input_names}
            )[0]
            embeddings.append(mean_pool(output, inputs["attention_mask"])[0])
        return np.asarray(embeddings, dtype=np.float32).reshape(-1, 384)
