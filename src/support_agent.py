import os
import re

from dotenv import load_dotenv
from google import genai

from src.retriever import SupportRetriever

load_dotenv()

SIMILARITY_THRESHOLD = 0.6
MODEL_NAME = "gemini-2.5-flash"


class SupportAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        self.client = genai.Client(api_key=api_key)
        self.retriever = SupportRetriever()

    def split_queries(self, query):
        """
        Split a message containing multiple questions into separate questions.
        """
        questions = re.split(r"\?\s*", query)
        cleaned_questions = []

        for question in questions:
            question = question.strip(" \"'\n\t")

            if question:
                cleaned_questions.append(question)

        return cleaned_questions

    def generate_response(self, query, results=None, top_k=3):
        queries = self.split_queries(query)

        if not queries:
            return "Please enter a valid customer support question."

        if len(queries) == 1:
            return self._generate_single_response(
                queries[0],
                results=results,
                top_k=top_k,
            )

        return self._generate_multi_response(queries, top_k=top_k)

    def _generate_single_response(self, query, results=None, top_k=3):
        if results is None:
            results = self.retriever.search(query, top_k=top_k)

        if not results:
            return self._fallback_response()

        best_score = results[0]["similarity"]

        print("\n" + "=" * 60)
        print("RETRIEVAL INFORMATION")
        print("=" * 60)
        print("Query:", query)
        print("Best similarity score:", round(best_score, 4))
        print("Similarity threshold:", SIMILARITY_THRESHOLD)
        print("Retrieved cases:", len(results))

        if best_score < SIMILARITY_THRESHOLD:
            print("Confidence: LOW")
            return self._fallback_response()

        print("Confidence: HIGH")

        examples = self._format_examples(results)
        prompt = f"""
You are a helpful customer support agent.

Use the historical support examples below as guidance.

Generate a concise, polite and natural response to the customer's
current query.

Important rules:

* Answer only using information supported by the historical examples.
* Do not copy the examples word-for-word.
* Do not invent policies, refunds, dates, order details, or account information.
* Do not promise an action that you cannot perform.
* If the issue requires account-specific information, direct the customer
  to the appropriate support team.
* Keep the response to 1-3 sentences.
* Do not mention the historical examples.
* Do not mention similarity scores or retrieval.

Historical support examples:
{examples}

Current customer query:
{query}

Final support response:
"""

        return self._create_completion(
            prompt,
            (
                "You are a helpful customer support agent. "
                "Follow the user's instructions and use only "
                "the provided support examples."
            ),
            max_completion_tokens=300,
            fallback_response=self._retrieved_fallback(results),
        )

    def _generate_multi_response(self, queries, top_k=3):
        print("\n" + "=" * 60)
        print("MULTI-QUESTION RETRIEVAL")
        print("=" * 60)

        all_questions = []
        all_examples = []
        fallback_answers = []
        question_number = 1

        for question in queries:
            print("\nProcessing question:", question)

            question_results = self.retriever.search(question, top_k=top_k)

            if not question_results:
                continue

            best_score = question_results[0]["similarity"]
            print("Best similarity:", round(best_score, 4))

            if best_score < SIMILARITY_THRESHOLD:
                print("Confidence: LOW")
                continue

            print("Confidence: HIGH")

            all_questions.append(f"{question_number}. {question}")
            all_examples.append(
                self._format_examples(
                    question_results,
                    prefix=f"Question {question_number} - ",
                )
            )
            fallback_answers.append(
                f"{question_number}. {self._retrieved_fallback(question_results)}"
            )
            question_number += 1

        if not all_questions:
            return self._fallback_response()

        questions_text = "\n".join(all_questions)
        examples_text = "\n".join(all_examples)

        prompt = f"""
You are a helpful customer support agent.

The customer has asked multiple questions.

Answer each relevant question separately using the historical
support examples provided below.

Important rules:

* Give one answer for each numbered customer question.
* Keep the same order as the questions.
* Answer only using information supported by the historical examples.
* Do not copy the examples word-for-word.
* Do not invent policies, refunds, dates, order details, or account information.
* Do not promise an action that you cannot perform.
* If an issue requires account-specific information, direct the customer
  to the appropriate support team.
* Keep each answer concise and natural.
* Do not mention historical examples.
* Do not mention similarity scores or retrieval.
* Do not combine unrelated questions into one answer.

Customer questions:
{questions_text}

Historical support examples:
{examples_text}

Final support response:
"""

        return self._create_completion(
            prompt,
            (
                "You are a helpful customer support agent. "
                "Answer only using the provided support information."
            ),
            max_completion_tokens=500,
            fallback_response="\n".join(fallback_answers),
        )

    def _create_completion(
        self,
        prompt,
        system_message,
        max_completion_tokens,
        fallback_response=None,
    ):
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=f"{system_message}\n\n{prompt}",
                config={
                    "temperature": 0.2,
                    "max_output_tokens": max_completion_tokens,
                },
            )

            answer = response.text

            if not answer:
                return "Sorry, I was unable to generate a response."

            return answer.strip()

        except Exception as e:
            print("\nGemini error:", e)

            if fallback_response:
                return fallback_response

            return "Sorry, I am currently unable to process your request."

    def _format_examples(self, results, prefix=""):
        examples = []

        for i, result in enumerate(results, start=1):
            examples.append(
                f'{prefix}Example {i}:\n'
                f'Customer: {result["query"]}\n'
                f'Agent: {result["response"]}'
            )

        return "\n\n".join(examples)

    def _retrieved_fallback(self, results):
        if not results:
            return self._fallback_response()

        response = results[0].get("response", "").strip()

        if response:
            return self._clean_retrieved_response(response)

        return self._fallback_response()

    def _clean_retrieved_response(self, response):
        response = re.sub(r"\s+", " ", response).strip()
        response = re.sub(r"\s+here:\s*\??\s*", " ", response, flags=re.IGNORECASE)
        response = re.sub(r"\s*\d+/\d+\s*$", "", response).strip()
        response = re.sub(
            r"\bHave you reported this to our support team\b",
            "Please report this to our support team",
            response,
            flags=re.IGNORECASE,
        )
        response = re.sub(r"\s+([,.!?])", r"\1", response)

        if response and response[-1] not in ".!?":
            response += "."

        return response

    def _fallback_response(self):
        return (
            "I'm sorry, but I don't have enough relevant information "
            "to confidently answer this request. Please provide more "
            "details or contact customer support."
        )


if __name__ == "__main__":
    agent = SupportAgent()
    query = input("\nEnter customer query: ").strip()

    if not query:
        print("Please enter a customer support question.")
    else:
        answer = agent.generate_response(query)

        print("\n" + "=" * 60)
        print("AI SUPPORT RESPONSE")
        print("=" * 60)
        print(answer)
