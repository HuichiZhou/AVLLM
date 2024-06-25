import torch
from flask import Flask, request
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('--device', type=int, default=2)
parser.add_argument('--model_path', type=str, default='model_path')
parser.add_argument('--port', type=int, default=6000)
args = parser.parse_args()

model_name = args.model_path
device = f'cuda:{args.device}'

print('-'*100)
print('model_path', model_name)
print('device', device)
print('port', args.port)
print('-'*100)

app = Flask(__name__)
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
# tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device, torch_dtype=torch.bfloat16)

gen_config = GenerationConfig(
                num_beams=1,
                do_sample=True,
                max_new_tokens=256,
                min_new_tokens=16,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                temperature=0.9,
                top_p=0.95,
            )
print(tokenizer.special_tokens_map, tokenizer.pad_token)


@app.route("/", methods=['post'])
def hello_world():
    data = request.get_json()
    print(data, type(data))
    data: list[str] = data['prompt']
    assert not data[0].endswith('Reason:')
    prompt = [item + '\nReason:' for item in data]
    inputs = tokenizer(prompt, return_tensors="pt", max_length=256, truncation=True, padding=True)
    outs = model.generate(**inputs.to(args.device), generation_config=gen_config)
    decode_outs = tokenizer.batch_decode(outs, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    print(decode_outs)
    return {'output': decode_outs}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=False)
    



