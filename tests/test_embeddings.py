import unittest

import numpy as np

from src.embeddings import mean_pool


class EmbeddingTests(unittest.TestCase):
    def test_pooling_ignores_padding_and_normalizes_for_cosine_search(self):
        tokens = np.array([[[3, 0], [0, 4], [99, 99]]], dtype=np.float32)
        result = mean_pool(tokens, np.array([[1, 1, 0]]))
        np.testing.assert_allclose(result, [[0.6, 0.8]], atol=1e-6)
        self.assertEqual(result.dtype, np.float32)

    def test_pooling_handles_an_empty_attention_mask_without_nan(self):
        result = mean_pool(np.ones((1, 2, 3)), np.zeros((1, 2)))
        np.testing.assert_array_equal(result, [[0, 0, 0]])


if __name__ == "__main__":
    unittest.main()
