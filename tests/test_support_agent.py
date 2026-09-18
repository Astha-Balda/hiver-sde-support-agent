import unittest
from unittest.mock import patch

from src.support_agent import SupportAgent


class SupportAgentTests(unittest.TestCase):
    def make_agent(self, search_results=None, generate_error=None):
        agent = SupportAgent.__new__(SupportAgent)
        agent.retriever = unittest.mock.Mock()
        agent.retriever.search.return_value = search_results or []
        agent.client = unittest.mock.Mock()

        if generate_error:
            agent.client.models.generate_content.side_effect = generate_error
        else:
            response = unittest.mock.Mock()
            response.text = "Generated answer"
            agent.client.models.generate_content.return_value = response

        return agent

    def test_split_queries_separates_questions_and_drops_blanks(self):
        agent = SupportAgent.__new__(SupportAgent)

        self.assertEqual(
            agent.split_queries('Where is my order? "Can I get a refund?" ?'),
            ["Where is my order", "Can I get a refund"],
        )

    def test_init_uses_gemini_api_key(self):
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}, clear=True),
            patch("src.support_agent.genai.Client") as client,
            patch("src.support_agent.SupportRetriever") as retriever,
        ):
            agent = SupportAgent()

        self.assertIsNotNone(agent.client)
        client.assert_called_once_with(api_key="fake-key")
        retriever.assert_called_once_with()

    def test_generate_response_accepts_relevant_medium_similarity_match(self):
        agent = self.make_agent(
            search_results=[
                {
                    "similarity": 0.6411,
                    "query": "This is what you got when you ordered Adidas shoes.",
                    "response": "Please contact our support team for help with this order.",
                }
            ]
        )

        answer = agent.generate_response("where is my adidas shoe")

        self.assertEqual(answer, "Generated answer")

    def test_generate_response_uses_retrieved_fallback_when_llm_fails(self):
        agent = self.make_agent(
            search_results=[
                {
                    "similarity": 1.0,
                    "query": "where is my order",
                    "response": (
                        "Please contact our support team here: so that we can "
                        "help with this order. 1/2"
                    ),
                }
            ],
            generate_error=RuntimeError("API key not valid"),
        )

        answer = agent.generate_response("where is my order")

        self.assertEqual(
            answer,
            "Please contact our support team so that we can help with this order.",
        )

    def test_retrieved_fallback_rewrites_stripped_support_link_question(self):
        agent = SupportAgent.__new__(SupportAgent)

        answer = agent._retrieved_fallback(
            [
                {
                    "response": (
                        "I'm terribly sorry for this situation. Have you "
                        "reported this to our support team here: ? 1/2"
                    )
                }
            ]
        )

        self.assertEqual(
            answer,
            "I'm terribly sorry for this situation. Please report this to our support team.",
        )


if __name__ == "__main__":
    unittest.main()
