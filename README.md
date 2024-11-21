##  Evaluating the Validity of Word-level Adversarial Attacks with Large Language Models

<h5 align=center>

[![Paper](https://aclanthology.org/images/acl-logo.svg)](https://aclanthology.org/2024.findings-acl.292/)


</h5>


## AVLLM

This guide provides detailed steps for fully fine-tuning the AVLLM model using the LLaMA Factory framework.   
Follow these instructions to set up your environment, prepare your model and datasets, and perform fine-tuning and evaluations.

## Environment Setup

1. **Clone the LLaMA Factory Repository**

   Clone the repository to your home directory:  
   ```python
   git clone https://github.com/hiyouga/LLaMA-Factory.git
   ```

2. **Create and Activate a Conda Environment**

   Create a new Conda environment named AVLLM and activate it:  
   ```python
   conda create -n AVLLM python=3.10  
   conda activate AVLLM  
   ```

3. **Install Dependencies**

   Navigate to the LLaMA-Factory directory and install the required dependencies:  
   ```python
   cd LLaMA-Factory  
   pip install -r requirements.txt
   ```
## Model and Data Preparation

1. **Download the Model**

   Download the TinyLlama model from Hugging Face and place it in the `model_path` directory:
   - Model URL: [TinyLlama-1.1B-intermediate-step-1431k-3T](https://huggingface.co/TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T)

2. **Prepare the Datasets**

   Download your fine-tuning dataset `AVLLM_train.json` and testing dataset `AVLLM_test.json`. Load these datasets into the `LLaMA-Factory/data` directory and update the `dataset_info.json` file to include:
   ```json
   "AVLLM-train": {
   "file_name": "AVLLM_train.json"
   },
   "AVLLM-test": {
   "file_name": "AVLLM_test.json"
   }
   ```
## Fine-Tuning

1. **Configure the Fine-Tuning Script**  

   In the `llama_factory` directory, create or modify the `full-ft.sh` script.
   

2. **Configure DeepSpeed**  
   Create or modify the `deepspeed.json` file.  
   
3. **Execute the Fine-Tuning Script**  
   Run the fine-tuning script:  
   ```python
   sh full-ft.sh  
   ```
## Adversarial Attack Module Setup

1. **Install TextAttack**   
   Install TextAttack for generating adversarial examples:  
   ```python
   pip install textattack
   ```  
2. **Generate Adversarial Examples**  
   Use the following command to generate adversarial examples for evaluation:  
   ```python
   sh generate_example.sh
   ```  
3. **Prepare Evaluation Data**  

   -Store the generated adversarial examples as `attack_example.csv`.  
   -Process this file using data_processing.py to format it for AVLLM inference.  
   -Load the resulting `evaluation.json` into the `LLaMA-Factory/data directory` and update `dataset_info.json`:  
   
   ```json
   "AVLLM-evaluation": {
   "file_name": "evaluation.json"
   }
   ```
4. **Run Inference and Evaluation**

   Use the `predict.sh` script for inference, and then evaluate the ASR with `evaluation.py`.   
   ```python
   sh predict.sh  
   python evaluation.py  
   ```
## Patch Module Setup

1. **Add Custom Module**  
   Place your module in `textattack/constraints/semantics/tinyllama.py` and update `textattack/attack_args.py` to include your module in the `CONSTRAINT_CLASS_NAMES`:
   ```python
   "tinyllama": "textattack.constraints.semantics.Tinyllama"
   ```
2. **API Call Setup**  
   Set up an API call by running `server.py` and adjust the address in `tinyllama.py` accordingly.  
   ```python
   python server.py
   ```
3. **Run Attack Command**  
   Execute the following command to run your attack module:
   ```python
   sh patch.sh  
   ```

## 📝 Citation

If you find this paper useful, please consider staring 🌟 this repo and citing 📑 our paper:

```
@inproceedings{zhou2024evaluating,
  title={Evaluating the validity of word-level adversarial attacks with large language models},
  author={Zhou, Huichi and Wang, Zhaoyang and Wang, Hongtao and Chen, Dongping and Mu, Wenhan and Zhang, Fangyuan},
  booktitle={Findings of the Association for Computational Linguistics ACL 2024},
  pages={4902--4922},
  year={2024}
}
```
