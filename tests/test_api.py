import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient

from src import api


class ApiTests(unittest.TestCase):
    def test_concurrent_first_requests_only_load_one_agent(self):
        cache = getattr(api, "_load_agent", api.get_agent)
        cache.cache_clear()
        created = []
        barrier = threading.Barrier(4)

        def build_agent():
            agent = object()
            created.append(agent)
            time.sleep(0.03)
            return agent

        def first_request(_):
            barrier.wait()
            return api.get_agent()

        try:
            with patch("src.api.SupportAgent", side_effect=build_agent):
                with ThreadPoolExecutor(max_workers=4) as executor:
                    results = list(executor.map(first_request, range(4)))
            self.assertEqual(len(created), 1)
            self.assertTrue(all(agent is results[0] for agent in results))
        finally:
            cache.cache_clear()

    def test_health_and_preflight_do_not_initialize_the_agent(self):
        with patch("src.api.SupportAgent", side_effect=AssertionError("loaded model")):
            with TestClient(api.app) as client:
                self.assertEqual(client.get("/").status_code, 200)
                response = client.options("/support", headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers["access-control-allow-origin"],
                "http://localhost:5173",
            )


if __name__ == "__main__":
    unittest.main()
