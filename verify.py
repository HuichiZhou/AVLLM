from Continuous import verify
# 获取文件夹中的所有jsonl文件
import os
import json
import ast


level = 2
folder_path = f'./GPT-4/{level}constraints_final_prompt_with_output'
files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0][6:]))

count = 0
for i in range(10):
    path = files[i]
    print(path)
    jsonl_file_path = os.path.join(folder_path, path)
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            flag = True
            lines = json.loads(line)
            output = str(lines['output'])
            uuid = ast.literal_eval(lines['uuid'])
            selected_vars = lines['selected_vars']

            for id in uuid:
                # print(id)
                vars = ast.literal_eval(selected_vars)[id]
                result = verify(output, vars, id)
                if not result:
                    flag = False
            if flag:
                count += 1
                
print(count/10)


