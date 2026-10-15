import unittest
from unittest.mock import patch

from google.genai import types

from src.support_agent import SupportAgent


class SupportAgentTests(unittest.TestCase):
    def response(self, text, finish_reason=types.FinishReason.STOP):
        return types.GenerateContentResponse(candidates=[types.Candidate(
            content=types.Content(parts=[types.Part(text=text)]),
            finish_reason=finish_reason,
        )])

    def make_agent(self, search_results=None, generate_error=None):
        agent = SupportAgent.__new__(SupportAgent)
        agent.retriever = unittest.mock.Mock()
        agent.retriever.search.return_value = search_results or []
        agent.client = unittest.mock.Mock()

        if generate_error:
            agent.client.models.generate_content.side_effect = generate_error
        else:
            agent.client.models.generate_content.return_value = self.response("Generated answer")

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

    def test_support_generation_reserves_output_budget_for_the_visible_answer(self):
        agent = self.make_agent(search_results=[{
            "similarity": 0.9,
            "query": "Where is my order?",
            "response": "Please contact support for help with your order.",
        }])
        agent.generate_response("Where is my order?")
        config = agent.client.models.generate_content.call_args.kwargs["config"]
        config = types.GenerateContentConfig.model_validate(config)
        self.assertIsNotNone(config.thinking_config)
        self.assertEqual(config.thinking_config.thinking_budget, 0)
        self.assertGreaterEqual(config.max_output_tokens, 512)

    def test_truncated_generation_is_retried_instead_of_returning_a_fragment(self):
        agent = self.make_agent()
        agent.client.models.generate_content.side_effect = [
            self.response("I apologize for the inconvenience. If", types.FinishReason.MAX_TOKENS),
            self.response("Please contact support for help with your order."),
        ]
        answer = agent._create_completion("Question", "Support agent", 512)
        self.assertEqual(answer, "Please contact support for help with your order.")
        calls = agent.client.models.generate_content.call_args_list
        self.assertEqual(len(calls), 2)
        first = types.GenerateContentConfig.model_validate(calls[0].kwargs["config"])
        second = types.GenerateContentConfig.model_validate(calls[1].kwargs["config"])
        self.assertGreater(second.max_output_tokens, first.max_output_tokens)

    def test_repeated_truncation_returns_the_fallback_after_one_retry(self):
        agent = self.make_agent()
        agent.client.models.generate_content.return_value = self.response(
            "A partial reply that ends with", types.FinishReason.MAX_TOKENS
        )
        answer = agent._create_completion(
            "Question", "Support agent", 512,
            fallback_response="Please contact support for help with your order.",
        )
        self.assertEqual(answer, "Please contact support for help with your order.")
        self.assertEqual(agent.client.models.generate_content.call_count, 2)

    def test_empty_generation_uses_the_available_support_fallback(self):
        agent = self.make_agent()
        agent.client.models.generate_content.return_value = self.response("")
        answer = agent._create_completion(
            "Question", "Support agent", 512,
            fallback_response="Please contact support for help with your order.",
        )
        self.assertEqual(answer, "Please contact support for help with your order.")


if __name__ == "__main__":
    unittest.main()
