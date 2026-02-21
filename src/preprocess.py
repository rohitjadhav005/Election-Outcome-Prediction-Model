import pandas as pd
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths
input_path = os.path.join(script_dir, "..", "data", "converted_data.csv")
output_path = os.path.join(script_dir, "..", "data", "clean_election.csv")

# Load your raw dataset
if not os.path.exists(input_path):
    print(f"Error: Input file not found at {input_path}")
    exit(1)

raw = pd.read_csv(input_path)

# Remove exact duplicate rows
raw = raw.drop_duplicates()

# Standardize party names
party_map = {
    "INC(I)": "INC",
    "Shiv Sena (UBT)": "SS",
    "Shiv Sena (Shinde)": "SS",
    "Shiv Sena": "SS",
    "NCP (Ajit)": "NCP",
    "NCP (SP)": "NCP"
}

raw["party"] = raw["party"].replace(party_map)

# Keep only one row per year-party
# We need to be careful with groupby/first if we want to keep specific data. 
# The user code: raw = raw.groupby(["year", "party"]).first().reset_index()
# This will take the first occurrence of mla_strength etc for that year/party.
raw = raw.groupby(["year", "party"]).first().reset_index()

# Encode candidate type
# The user provided map: {"new": 0, "mixed": 1, "incumbent": 2}
# Note: In converted_data.csv, candidate_type is "new", "mixed", "incumbent".
candidate_map = {"new": 0, "mixed": 1, "incumbent": 2}
# Handle potential case sensitivity or missing values if needed, but assuming data is clean enough per user code
raw["candidate_type"] = raw["candidate_type"].map(candidate_map)

# Fix winner column: only max MLA strength wins per year
raw["winner"] = 0
for year in raw["year"].unique():
    # Find the index of the row with max mla_strength for this year
    # We need to make sure we are looking at the relevant rows
    year_data = raw[raw["year"] == year]
    if not year_data.empty:
        idx = year_data["mla_strength"].idxmax()
        raw.loc[idx, "winner"] = 1

# Sort nicely
raw = raw.sort_values(["year", "mla_strength"], ascending=[True, False])

# Save clean dataset
raw.to_csv(output_path, index=False)

print(f"✅ Clean dataset saved as {output_path}")
print(raw.head())
print("\nColumns:", raw.columns.tolist())
print("Candidate Type unique values:", raw["candidate_type"].unique())
