import replicate
import json
import os
import time  # 用于重试间隔
from datasets import load_dataset
from api import get_gpt_res
import random 
from system_prompt import stage2_prompt

def load_alpaca_dataset(data_path, n, m):
    alpaca_dataset = load_dataset(data_path)
    
    train_instructions = alpaca_dataset['train']['instruction']
    train_inputs = alpaca_dataset['train']['input']
    filtered_indices = []

    for i in range(len(train_instructions)):
        if train_instructions[i] is not None and train_inputs[i]=='':
            filtered_indices.append(i)

    filtered_instructions = [train_instructions[i] for i in filtered_indices]
    base_questions = filtered_instructions[n:m]
    
    return base_questions

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


def single_meta_prompt(data_path, base_questions, constraints_pool, system_prompt, number):
    single_constraint_prompt=[]
    with open(data_path, "w") as file:
        for i in range(0, number):
            success = False
            while not success:
                existing_category={}
                constraints_few_shot = constraint_from_list(constraints_pool, sample_size=5, existing_category = existing_category)
                filtered_constraints = [
                    {'uuid': constraint['uuid'], 
                    'category': constraint['category'],
                    'constraint': constraint['constraint'], 
                    'vars': constraint['vars']}
                    for constraint in constraints_few_shot
                ]
                prompt_sample = base_questions[i]
                question = "# Question \n" + prompt_sample + '\n# Constraint pool\n' + str(filtered_constraints)
                print(question)
                verifiable_prompt = get_gpt_res(question, 'gpt-4', system_prompt)
                verifiable_prompt = json.loads(verifiable_prompt)
                single_constraint_prompt.append(verifiable_prompt)
                print(verifiable_prompt)
                file.write(json.dumps(verifiable_prompt))
                file.write("\n")
                success = True  
            
    file.close()


choices = False
system_prompt_stage2 = stage2_prompt()
constraints_pool=[]
with open("constraint_pool.jsonl", 'r', encoding = 'utf-8') as file:
        for line in file:
            constraint = json.loads(line)
            constraints_pool.append(constraint)
initial_number = 0
prompt_number = 10

n_level = 4

if choices:
    base_question = load_alpaca_dataset("/media/ssd/zhc/UNC/Instruction-tuning/data", initial_number, prompt_number)
    base_meta_prompt = single_meta_prompt("GPT-4_meta_prompt_level-1.jsonl", base_question, constraints_pool, system_prompt_stage2, prompt_number)
    print(base_meta_prompt)
else:
    folder_path = f'./GPT-4/{n_level - 1}constraints_final_prompt'  # Replace with your folder path

    json_list = []

    # Get all files in the folder and sort by filename
    file_names = sorted([f for f in os.listdir(folder_path) if f.endswith('.jsonl')])
    # Read the JSON files in sorted order
    for filename in file_names:
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)  # Load JSON data
            json_list.append(json_data)  

    base_question = [json_list[i]['final_prompt'] for i in range(prompt_number)]
    base_meta_prompt = single_meta_prompt(f"GPT-4_meta_prompt_level-{n_level}.jsonl", base_question, constraints_pool, system_prompt_stage2, prompt_number)
    