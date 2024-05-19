import json
from api import get_gpt_res
import random
import os
from system_prompt import stage2_prompt

def constraint_from_list(input_list, sample_size, existing_category):
    if sample_size <= 0:
        print("Sample size must be positive.")
        return None
    filtered_list = [item for item in input_list if item['category'] not in existing_category]
    if sample_size > len(filtered_list):
        print("Sample size exceeds the length of the filtered list. Returning the whole filtered list.")
        return filtered_list
    else:
        return random.sample(filtered_list, sample_size)


def generate_verifiable_prompts(n, m, existing_category, constraints_pool, single_constraint_prompt, system_prompt):
    existing_category = {existing_category}
    updated_prompt = single_constraint_prompt["new_prompt"]
    verifiable_prompt = {
        "base_question": single_constraint_prompt["base_question"],
        "new_prompt": single_constraint_prompt["new_prompt"],
        "variable": [single_constraint_prompt["variable"]]
    }
    for _ in range(n):
        constraints_few_shot = constraint_from_list(constraints_pool, m, existing_category)
        
        if not constraints_few_shot:  # If no new unique constraints could be sampled, break to avoid infinite loop
            break
        
        filtered_constraints = [
                    {'uuid': constraint['uuid'], 
                    'category': constraint['category'],
                    'constraint': constraint['constraint'], 
                    'vars': constraint['vars']}
                    for constraint in constraints_few_shot
                ]

        # Combine sampled constraints into one question for GPT
        question = "# Question \n" + updated_prompt + '\n# Constraint pool\n' + str(filtered_constraints) 
        # print(question)
        
        # Ask GPT to choose the best fitting constraint and update the prompt
        response = json.loads(get_gpt_res(question, 'gpt-4', system_prompt))
        # print(response)
        
        verifiable_prompt["variable"].append(response["variable"])
        updated_prompt = response["new_prompt"]
        existing_category.add(response["category"])
        # print(existing_category)
    verifiable_prompt["new_prompt"] = updated_prompt
    # print(verifiable_prompt)
    return verifiable_prompt


level = 2

base_meta_prompt_path = f"GPT-4_meta_prompt_level-{level}.jsonl"

single_constraint_prompt=[]
with open(base_meta_prompt_path, 'r', encoding = 'utf-8') as file:
        for line in file:
            meta_prompt = json.loads(line)
            single_constraint_prompt.append(meta_prompt)
            
# print(single_constraint_prompt)

constraints_pool=[]
with open("constraint_pool.jsonl", 'r', encoding = 'utf-8') as file:
        for line in file:
            constraint = json.loads(line)
            constraints_pool.append(constraint)


n = 0  # Number of new constraints to add
m = 5  # Number of constraints to sample for GPT to choose from



system_prompt_stage2 = stage2_prompt()

verifiable_prompts=[]
for _ in range(len(single_constraint_prompt)):
    if "category" in single_constraint_prompt[_]:
        existing_uuid = single_constraint_prompt[_]["category"]
        # Generate verifiable prompts
        values = generate_verifiable_prompts(n, m, existing_uuid, constraints_pool, single_constraint_prompt[_], system_prompt_stage2)
        verifiable_prompts.append(values)


directory = f"GPT-4/{n+level}constraints"
if not os.path.exists(directory):
    os.makedirs(directory)
    
i=1
for dict_item in verifiable_prompts:
    # Construct the file name using the uuid of the dictionary
    file_name = f"prompt{i}.json"
    # Full path for the file
    file_path = os.path.join(directory, file_name)
    
    # Write the dictionary to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(dict_item, json_file, indent = 4)
    i+=1
    
