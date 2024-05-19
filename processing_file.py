import json
import os

for i in range(1,4):
    # Paths to the directories
    dir1 = f'GPT-4/{i}constraints_final_prompt'
    dir2 = f'GPT-4/{i+1}constraints_final_prompt'

    # Get the common filenames from both directories
    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))
    common_files = files1.intersection(files2)

    # Function to merge lists and keep unique values
    def merge_unique_lists(list1, list2):
        return list(set(list1) | set(list2))

    # Loop through the common files to merge data, keeping other keys intact
    for file_name in common_files:
        # Load the first file's data
        with open(os.path.join(dir1, file_name), "r") as f:
            data1 = [json.loads(line) for line in f]

        # Load the second file's data
        with open(os.path.join(dir2, file_name), "r") as f:
            data2 = [json.loads(line) for line in f]

        # Convert 'selected_vars' to dictionaries
        data1_uuids = eval(data1[0]["uuid"])
        data2_uuids = eval(data2[0]["uuid"])
        
        data1_selected_vars = eval(data1[0]["selected_vars"])
        data2_selected_vars = eval(data2[0]["selected_vars"])

        # Merge 'uuid' with unique values
        updated_uuids = merge_unique_lists(data1_uuids, data2_uuids)

        # Merge 'selected_vars' by combining values and keeping unique
        updated_selected_vars = data2_selected_vars.copy()
        for key, values in data1_selected_vars.items():
            if key in updated_selected_vars:
                updated_selected_vars[key] = merge_unique_lists(updated_selected_vars[key], values)
            else:
                updated_selected_vars[key] = values

        # Update 'uuid' and 'selected_vars' in the second file's data
        data2[0]["uuid"] = str(updated_uuids)
        data2[0]["selected_vars"] = str(updated_selected_vars)

        # Save the updated data back to the second file
        with open(os.path.join(dir2, file_name), "w") as f:
            for item in data2:
                f.write(json.dumps(item) + "\n")
