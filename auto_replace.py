import json
import random
import os

def replace_VAR(constraint_num, prompt_path, constraint_path):
    '''
    Args:
    - constraint_num: The number of constraints in the prompt.
    - prompot_path: The files to be processed, each file contains a prompt.
    - constraint_path: The file storing constraints.
    '''
    with open(prompt_path, 'r', encoding = 'utf-8') as file:
        data_dict = json.load(file)
    prompt = data_dict["new_prompt"]
    variable = data_dict["variable"]
    uuids = [item["uuid"] for item in variable]
    selections = {}
    parameters = {}
    
    for _ in range(constraint_num):
        parameters[uuids[_]] = []
        with open(constraint_path, 'r', encoding = 'utf-8') as file:
            # Retrieve the required constraint.
            for line_number, line in enumerate(file):
                if line_number == uuids[_]:
                    constraint = json.loads(line)
                    break
        # Save all the candidate vars.
        vars = [ x["values"] for x in constraint["vars"] ]
        i = 0
        try:
            for var in variable[_]["variable_name"]:
                # "Var" refers to the locations to be replaced, and "select" refers to the values chosen for replacement.
                select = str(random.choice(vars[i]))
                selections[var] = select
                i += 1
                prompt = prompt.replace(var, select)
                parameters[uuids[_]].append(select)
        except Exception as e:
            print("An exception occurred.")
            break
    return prompt, selections, uuids, parameters

def replace_vars_with_values(constraint_num, constraint_path):
    dic_path = f"./GPT-4/{constraint_num}constraints/"
    dic_path_new = f"./GPT-4/{constraint_num}constraints_final_prompt/"
    if not os.path.exists(dic_path_new):
        os.makedirs(dic_path_new)

    original_prompts= []  
    prompts = []
    selections = []
    uuids = []
    parameters = []
    
    # Sort all the files to be processed to ensure that the order of files in the input and output folders is consistent.
    files = sorted(os.listdir(dic_path), key=lambda x: int(x.split('.')[0][6:]))
    for file in files:
        cur_file= os.path.join(dic_path, file)
        with open(cur_file, 'r', encoding = 'utf-8') as file:
            original_prompts.append(json.load(file)["new_prompt"])
        res = replace_VAR(1, cur_file, constraint_path)
        prompts.append(res[0])
        selections.append(res[1])
        uuids.append(res[2])
        parameters.append(res[3])
        
    
    
    for i in range(len(prompts)):
        file_name = f"prompt{i+1}.txt"
        # Full path for the file
        file_path = os.path.join(dic_path_new, file_name)
        
        with open(file_path, 'w') as file:
            file.write(str(uuids[i]))
            file.write("\n")
            file.write(original_prompts[i])
            file.write("\n")
            file.write(str(selections[i]))
            file.write("\n")
            file.write(prompts[i])
            file.write("\n")
            file.write(str(parameters[i]))
            


def txt2json(folder_path):
    # 获取文件夹中的所有txt文件
    txt_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.txt')])

    # 遍历每个txt文件
    for txt_file in txt_files:
        # 构建txt文件的完整路径
        txt_file_path = os.path.join(folder_path, txt_file)

        # 读取txt文件的内容
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 检查文件行数是否足够
        if len(lines) >= 5:
            # 创建字典存储jsonl文件的数据
            json_data = {
                'uuid': lines[0].strip(),
                'meta_prompt': lines[1].strip(),
                'vars': lines[2].strip(),
                'final_prompt': lines[3].strip(),
                'selected_vars': lines[4].strip()
            }

            # 构建jsonl文件的路径
            jsonl_file_path = os.path.join(folder_path, txt_file.replace('.txt', '.jsonl'))

            # 将json数据写入jsonl文件
            with open(jsonl_file_path, 'w', encoding='utf-8') as jsonl_file:
                json.dump(json_data, jsonl_file)
                jsonl_file.write('\n')

            # 删除原始txt文件
            os.remove(txt_file_path)
        else:
            print(f'Error: File {txt_file} does not have enough lines')


level = 2
replace_vars_with_values(level, "constraint_pool.jsonl")
txt2json(f'GPT-4/{level}constraints_final_prompt')