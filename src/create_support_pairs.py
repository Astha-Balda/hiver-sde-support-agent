import json
import os


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

input_file = "data/processed/amazonhelp_cleaned.jsonl"

output_file = "data/processed/amazonhelp_support_pairs.jsonl"


# --------------------------------------------------
# 2. Create support pairs
# --------------------------------------------------

print("Creating customer-support pairs...")

pair_count = 0
conversation_count = 0
skipped_customer_messages = 0

os.makedirs("data/processed", exist_ok=True)


with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_file, "w", encoding="utf-8") as outfile:

    for line in infile:

        if not line.strip():
            continue

        conversation = json.loads(line)

        messages = conversation["messages"]

        conversation_count += 1

        # Go through every message
        for i in range(len(messages)):

            current_message = messages[i]

            # We only start a pair with a customer message
            if not current_message["inbound"]:
                continue

            query = current_message["text"].strip()

            # Find the next AmazonHelp response
            response = None

            for j in range(i + 1, len(messages)):

                next_message = messages[j]

                if not next_message["inbound"]:

                    response = next_message["text"].strip()
                    break

            # Skip if no agent response exists
            if not response:

                skipped_customer_messages += 1
                continue

            pair = {
                "conversation_id": conversation["conversation_id"],
                "query": query,
                "response": response
            }

            outfile.write(
                json.dumps(
                    pair,
                    ensure_ascii=False
                ) + "\n"
            )

            pair_count += 1


# --------------------------------------------------
# 3. Statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("SUPPORT PAIR RESULTS")
print("=" * 60)

print("Conversations processed:", conversation_count)
print("Support pairs created:", pair_count)
print("Customer messages without response:", skipped_customer_messages)

print("\nSaved support pairs to:")
print(output_file)

print("\nSupport pair creation complete!")