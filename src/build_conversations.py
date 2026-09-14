import pandas as pd
import json
import os

# --------------------------------------------------
# 1. Load the ORIGINAL dataset
# --------------------------------------------------

input_file = "data/raw/twcs.csv"

print("Loading original dataset...")

df = pd.read_csv(input_file)

print("Total tweets:", len(df))


# --------------------------------------------------
# 2. Make tweet IDs consistent
# --------------------------------------------------

df["tweet_id"] = df["tweet_id"].astype(str)

tweet_lookup = df.set_index("tweet_id").to_dict("index")


# --------------------------------------------------
# 3. Find tweets belonging to AmazonHelp
# --------------------------------------------------

brand = "AmazonHelp"

amazon_tweets = df[
    df["author_id"] == brand
]

print("\n" + "=" * 60)
print("AMAZONHELP DATA")
print("=" * 60)

print("AmazonHelp tweets:", len(amazon_tweets))


# --------------------------------------------------
# 4. Reconstruct conversation
# --------------------------------------------------

def get_conversation(tweet_id):

    conversation = []

    current_id = str(tweet_id)

    visited = set()

    while current_id in tweet_lookup and current_id not in visited:

        visited.add(current_id)

        tweet = tweet_lookup[current_id]

        conversation.append({
            "tweet_id": current_id,
            "author_id": tweet["author_id"],
            "inbound": bool(tweet["inbound"]),
            "created_at": tweet["created_at"],
            "text": tweet["text"]
        })

        parent_id = tweet["in_response_to_tweet_id"]

        if pd.isna(parent_id):
            break

        current_id = str(int(float(parent_id)))

    # We traversed backwards,
    # so reverse to chronological order.
    conversation.reverse()

    return conversation


# --------------------------------------------------
# 5. Reconstruct conversations containing AmazonHelp
# --------------------------------------------------

print("\nBuilding conversations...")

conversations = {}

for tweet_id in amazon_tweets["tweet_id"]:

    conversation = get_conversation(tweet_id)

    # We need at least 2 messages
    if len(conversation) >= 2:

        root_id = conversation[0]["tweet_id"]

        conversations[root_id] = {
            "conversation_id": root_id,
            "messages": conversation
        }


conversations = list(conversations.values())


# --------------------------------------------------
# 6. Statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("CONVERSATION STATISTICS")
print("=" * 60)

print("Total conversations:", len(conversations))


if conversations:

    lengths = [
        len(c["messages"])
        for c in conversations
    ]

    print(
        "Average messages per conversation:",
        round(sum(lengths) / len(lengths), 2)
    )

    print(
        "Longest conversation:",
        max(lengths)
    )

    print(
        "Shortest conversation:",
        min(lengths)
    )


# --------------------------------------------------
# 7. Count customer/company messages
# --------------------------------------------------

total_customer_messages = 0
total_company_messages = 0

for conversation in conversations:

    for message in conversation["messages"]:

        if message["inbound"]:
            total_customer_messages += 1
        else:
            total_company_messages += 1


print("\nCustomer messages:", total_customer_messages)
print("Company messages:", total_company_messages)


# --------------------------------------------------
# 8. Show sample conversations
# --------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE CONVERSATIONS")
print("=" * 60)


for i, conversation in enumerate(conversations[:10]):

    print("\nConversation", i + 1)
    print("Conversation ID:", conversation["conversation_id"])

    for message in conversation["messages"]:

        if message["inbound"]:
            speaker = "CUSTOMER"
        else:
            speaker = "AMAZONHELP"

        print(f"[{speaker}] {message['text']}")


# --------------------------------------------------
# 9. Save conversations
# --------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

output_file = (
    "data/processed/amazonhelp_conversations.jsonl"
)

with open(output_file, "w", encoding="utf-8") as file:

    for conversation in conversations:

        file.write(
            json.dumps(
                conversation,
                ensure_ascii=False
            ) + "\n"
        )


print("\n" + "=" * 60)
print("SUCCESS")
print("=" * 60)

print("Saved conversations to:")
print(output_file)