import json
import re
from collections import Counter

# --------------------------------------------------
# 1. Load reconstructed conversations
# --------------------------------------------------

input_file = "data/processed/amazonhelp_conversations.jsonl"

print("Loading conversations...")

conversations = []

with open(input_file, "r", encoding="utf-8") as file:

    for line in file:
        conversations.append(json.loads(line))

print("Total conversations:", len(conversations))


# --------------------------------------------------
# 2. Extract customer messages
# --------------------------------------------------

customer_messages = []

for conversation in conversations:

    for message in conversation["messages"]:

        if message["inbound"]:

            customer_messages.append({
                "conversation_id": conversation["conversation_id"],
                "text": message["text"]
            })


print("Total customer messages:", len(customer_messages))


# --------------------------------------------------
# 3. Basic text cleaning
# --------------------------------------------------

def clean_text(text):

    text = str(text)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove @mentions
    text = re.sub(r"@\w+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


for message in customer_messages:

    message["clean_text"] = clean_text(message["text"])


# --------------------------------------------------
# 4. Show message length statistics
# --------------------------------------------------

lengths = [
    len(message["clean_text"])
    for message in customer_messages
]

print("\n" + "=" * 60)
print("MESSAGE STATISTICS")
print("=" * 60)

print("Average characters:",
      round(sum(lengths) / len(lengths), 2))

print("Shortest message:",
      min(lengths))

print("Longest message:",
      max(lengths))


# --------------------------------------------------
# 5. Search for common support keywords
# --------------------------------------------------

keyword_groups = {

    "delivery": [
        "delivery",
        "delivered",
        "deliver",
        "shipping",
        "shipped",
        "package",
        "parcel",
        "courier"
    ],

    "order": [
        "order",
        "orders",
        "ordered"
    ],

    "refund": [
        "refund",
        "refunded",
        "money back",
        "moneyback"
    ],

    "return": [
        "return",
        "returned"
    ],

    "payment": [
        "payment",
        "charged",
        "charge",
        "credit card",
        "debit card"
    ],

    "account": [
        "account",
        "login",
        "password",
        "sign in",
        "signin"
    ],

    "prime": [
        "prime",
        "prime video"
    ],

    "cancel": [
        "cancel",
        "cancelled",
        "canceled"
    ],

    "package_missing": [
        "missing",
        "lost",
        "never arrived",
        "didn't arrive",
        "did not arrive"
    ],

    "damaged": [
        "damaged",
        "broken",
        "damage"
    ],

    "preorder": [
        "preorder",
        "pre-order"
    ],

    "fire": [
        "fire tv",
        "firetv",
        "fire stick",
        "firestick"
    ],

    "alexa": [
        "alexa"
    ]
}


# --------------------------------------------------
# 6. Count keyword groups
# --------------------------------------------------

keyword_counts = Counter()

for message in customer_messages:

    text = message["clean_text"].lower()

    for category, keywords in keyword_groups.items():

        for keyword in keywords:

            if keyword in text:

                keyword_counts[category] += 1

                # Don't count the same category twice
                break


print("\n" + "=" * 60)
print("KEYWORD-BASED ISSUE DISTRIBUTION")
print("=" * 60)

for category, count in keyword_counts.most_common():

    print(f"{category:20} {count}")


# --------------------------------------------------
# 7. Show random-ish examples for each category
# --------------------------------------------------

print("\n" + "=" * 60)
print("EXAMPLES BY CATEGORY")
print("=" * 60)

for category, keywords in keyword_groups.items():

    examples = []

    for message in customer_messages:

        text = message["clean_text"].lower()

        if any(keyword in text for keyword in keywords):

            examples.append(message["clean_text"])

        if len(examples) == 5:
            break

    if examples:

        print("\n---", category.upper(), "---")

        for example in examples:
            print("-", example)


# --------------------------------------------------
# 8. Save cleaned customer messages
# --------------------------------------------------

output_file = "data/processed/amazonhelp_customer_messages.jsonl"

with open(output_file, "w", encoding="utf-8") as file:

    for message in customer_messages:

        file.write(
            json.dumps(
                message,
                ensure_ascii=False
            ) + "\n"
        )


print("\nSaved customer messages to:")
print(output_file)

print("\nIntent analysis complete!")