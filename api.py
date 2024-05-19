from openai import AzureOpenAI
import replicate
import json
import os
import time  # 用于重试间隔



def get_gpt_res(prompt, model, system_prompt):
    model_mapping = {'gpt-4': 'huichi-gpt-4', 'chatgpt': 'yuehuang-chatgpt'}
    client = AzureOpenAI(
        api_key='ad425fdf93014b4fa94edc0dca626337',
        api_version="2023-12-01-preview",
        azure_endpoint="https://yuehuang-gpt-4.openai.azure.com/"
    )
    chat_completion = client.chat.completions.create(
        model=model_mapping[model],
        messages=[
            {"role":"system", "content":system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" },
    )
    return chat_completion.choices[0].message.content

# 获取模型结果的函数
def get_llama_res(prompt, model, system_prompt):
    input = {
        "prompt": f"{prompt}",
        "prompt_template": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",

    }

    # 获取输出
    output = replicate.run(
        model,
        input=input
    )
    
    string = ''.join([i for i in output])  # 合并结果
    return string
