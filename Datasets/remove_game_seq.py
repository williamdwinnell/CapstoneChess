import json

# Input and output file paths
input_file = "./Datasets/low_elo_4287_games_training_engine_nosco.jsonl"
output_file = "./Datasets/low_elo_4287_games_training_engine_nosco_noseq.jsonl"

# Create a list to store modified entries
modified_entries = []

# Read the original JSONL file and process each entry
with open(input_file, "r") as infile:
    for line in infile:
        entry = json.loads(line)
        if "Game Sequence" in entry["input"]:
            # Remove the entire "Game Sequence" line
            lines = entry["input"].split('\n')
            modified_lines = [line for line in lines if not line.startswith("Game Sequence: ")]
            entry["input"] = '\n'.join(modified_lines)

        # Add the modified entry to the list
        modified_entries.append(entry)

# Write the modified entries to a new JSONL file
with open(output_file, "w") as outfile:
    for entry in modified_entries:
        # Write each modified entry as a JSONL line
        outfile.write(json.dumps(entry) + "\n")

print("Dataset has been modified and saved to", output_file)