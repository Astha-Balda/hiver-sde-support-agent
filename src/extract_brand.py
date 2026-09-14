import pandas as pd
import os

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

file_path = "data/raw/twcs.csv"

print("Loading dataset...")

df = pd.read_csv(file_path)

print("Total rows:", len(df))


# --------------------------------------------------
# 2. Select AmazonHelp
# --------------------------------------------------

brand = "AmazonHelp"

brand_df = df[df["author_id"] == brand].copy()

print("\n" + "=" * 60)
print("BRAND DATA")
print("=" * 60)

print("Brand:", brand)
print("Support tweets:", len(brand_df))


# --------------------------------------------------
# 3. Customer tweets related to AmazonHelp
# --------------------------------------------------

# A customer tweet usually mentions/replies to AmazonHelp,
# but its author_id is different from AmazonHelp.

customer_df = df[
    (df["inbound"] == True) &
    (df["text"].str.contains("AmazonHelp", case=False, na=False))
].copy()

print("Customer tweets mentioning AmazonHelp:", len(customer_df))


# --------------------------------------------------
# 4. Show examples
# --------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE AMAZONHELP SUPPORT TWEETS")
print("=" * 60)

print(
    brand_df[
        ["tweet_id", "author_id", "inbound", "text",
         "response_tweet_id", "in_response_to_tweet_id"]
    ].head(10).to_string(index=False)
)


print("\n" + "=" * 60)
print("SAMPLE CUSTOMER TWEETS")
print("=" * 60)

print(
    customer_df[
        ["tweet_id", "author_id", "inbound", "text",
         "response_tweet_id", "in_response_to_tweet_id"]
    ].head(10).to_string(index=False)
)


# --------------------------------------------------
# 5. Save AmazonHelp data
# --------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

output_file = "data/processed/amazonhelp.csv"

brand_df.to_csv(output_file, index=False)

print("\nSaved AmazonHelp data to:")
print(output_file)