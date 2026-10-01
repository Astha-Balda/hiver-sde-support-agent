import os

from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Reply to this customer support query in a helpful and concise way: "
            "My order has not arrived yet."
        ),
    )

    print(response.text)


if __name__ == "__main__":
    main()
