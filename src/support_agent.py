import os

from dotenv import load_dotenv
from google import genai

from src.retriever import SupportRetriever


load_dotenv()

SIMILARITY_THRESHOLD = 0.75


class SupportAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        self.client = genai.Client(api_key=api_key)
        self.retriever = SupportRetriever()

    def generate_response(self, query, results=None, top_k=3):
        
        # Retrieve only if results were not already provided
        if results is None:
            results = self.retriever.search(query, top_k=top_k)
            

        if not results:
            print("\nConfidence: LOW")
            return "Sorry, I could not find relevant support information."

        # Get best similarity score
        best_score = results[0]["similarity"]

        # Determine confidence
        if best_score >= SIMILARITY_THRESHOLD:
            confidence = "HIGH"
        else:
            confidence = "LOW"

        print("\n" + "=" * 60)
        print("RETRIEVAL INFORMATION")
        print("=" * 60)

        print("Best similarity score:", round(best_score, 4))
        print("Similarity threshold:", SIMILARITY_THRESHOLD)
        print("Confidence:", confidence)
        print("Retrieved cases:", len(results))

        # Low-confidence fallback
        if best_score < SIMILARITY_THRESHOLD:
            return (
                "I'm sorry, but I don't have enough relevant information "
                "to confidently answer this request. Please provide more "
                "details or contact customer support."
            )

        # Build historical examples
        examples = ""

        for i, result in enumerate(results, start=1):

            examples += f"""
Example {i}:
Customer: {result["query"]}
Agent: {result["response"]}
"""

        # Prompt Gemini
        prompt = f"""
You are a helpful customer support agent.

Use the historical support examples below as guidance.

Generate a concise, polite and natural response to the customer's
current query.

Important rules:
- Do not copy the examples word-for-word.
- Do not invent policies, refunds, dates, order details, or account information.
- Do not promise an action that you cannot perform.
- If the issue requires account-specific information, direct the customer
  to the appropriate support team.
- Avoid unnecessary repetition.
- Keep the response to 1-3 sentences.

Historical support examples:
{examples}

Current customer query:
{query}

Final support response:
"""

        # Generate response using Gemini
        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if not response.text:
                return "Sorry, I was unable to generate a response."

            return response.text.strip()

        except Exception as e:

            print("\nGemini error:", e)

            return "Sorry, I am currently unable to process your request."


if __name__ == "__main__":

    agent = SupportAgent()

    query = input("\nEnter customer query: ").strip()

    if not query:

        print("Please enter a customer query.")

    else:

        answer = agent.generate_response(query)

        print("\n" + "=" * 60)
        print("AI SUPPORT RESPONSE")
        print("=" * 60)

        print(answer)