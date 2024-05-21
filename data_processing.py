import csv
import json

file_path = 'attack_example.csv'

processed_data = []

with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row.get("result_type") == "Successful":
            processed_item = {
            "instruction": "You are a helpful assistant to analysis and rate the Semantic Similarity metric between two text samples: an original text and an adversarial text with changes like synonym substitutions and minor grammatical alterations. \n\n            Evaluation Criteria: Semantic Similarity (1-5) - This measures how closely the adversarial text aligns with the original in terms of meaning. Changes may include synonym substitutions and minor grammatical errors, highlighted with '[[' and ']]'. The score should reflect the degree to which the altered text preserves the original's meaning, where 5 signifies identical meaning and 1 indicates a completely different meaning.\n\n            Evaluation Steps:\n            1. Read both the original and adversarial text samples carefully.\n            2. Pay attention to the words or sentences modified in the adversarial sample, as indicated by ‘[[’ and ‘]]’.\n            3. Evaluate the extent to which the adversarial text maintains the semantic essence of the original.\n            4. Answer by starting to analyze the given example regarding the evaluation criteria as con cise as possible (no more than 50 words), and then give the numeric rating.\n\n            Question: On a scale of 1-5, where 5 is the highest, how similar is the adversarial text to the original in terms of semantic meaning? Your should follow the Evaluation Steps and rate based on Evaluation Criteria. Please adhering to the JSON format as shown in examples. Note that repetition of the provided sentences is unnecessary.",
            "input": "original_text: " + row["original_text"] + "\n" + "perturbed_text: " + row["perturbed_text"],
            "output": " "
            }
            processed_data.append(processed_item)

output_file_path = 'evaluation.json'
with open(output_file_path, 'w', encoding='utf-8') as outfile:
    json.dump(processed_data, outfile, ensure_ascii=False, indent=4)

print(f"Processed data has been saved to {output_file_path}")