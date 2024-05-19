import json
import os 

from api import get_gpt_res, get_llama_res
from system_prompt import inference_prompt

level = 4

prompt_system = inference_prompt()

# 文件夹路径，其中包含jsonl文件
folder_path = f'./GPT-4/{level}constraints_final_prompt'
destination_folder_path = f'./GPT-4/{level}constraints_final_prompt_with_output'

if not os.path.exists(destination_folder_path):
    os.makedirs(destination_folder_path)
    
# 获取文件夹中的所有jsonl文件
jsonl_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jsonl')])

model_name = True
if model_name:
    # 遍历每个jsonl文件
    for jsonl_file in jsonl_files:
        # 构建jsonl文件的完整路径
        jsonl_file_path = os.path.join(folder_path, jsonl_file)
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                lines = json.loads(line)
                prompt = lines['final_prompt']
                print(prompt)
                output = json.loads(get_gpt_res(prompt, 'gpt-4', prompt_system))
            # 将更新后的数据添加到新的列表中
            lines.update(output)
            
        destination_jsonl_file_path = os.path.join(destination_folder_path, jsonl_file)
        
        # 写入目标jsonl文件
        with open(destination_jsonl_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(lines) + '\n')  # 每行一个JSON对象
else:
    for jsonl_file in jsonl_files:
        # 构建jsonl文件的完整路径
        jsonl_file_path = os.path.join(folder_path, jsonl_file)

        # 检查目标文件是否存在
        destination_jsonl_file_path = os.path.join(destination_folder_path, jsonl_file)
        if os.path.exists(destination_jsonl_file_path):
            print(f"{jsonl_file} already exists, skipping.")
            continue  # 跳过这个文件

        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            print(jsonl_file_path)
            lines = [json.loads(line) for line in f]  # 将所有行转换为字典
            for item in lines:
                prompt = item['final_prompt']
                print(prompt)

                answer = get_llama_res(prompt, "meta/meta-llama-3-70b-instruct", prompt_system)  # 获取结果
                new_answer = {'output': answer}
                item.update(new_answer)  # 更新字典

                # 写入目标jsonl文件
                with open(destination_jsonl_file_path, 'w', encoding='utf-8') as wf:
                    json.dump(item, wf)  # 写入字典
                    wf.write('\n')
                
