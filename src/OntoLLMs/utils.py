import os
from datasets import load_from_disk
import json 
import random


def read_strategyqa():
    org_path='./data/OriginalDatasets/strategyqa_train.json'
    data = []
    with open(org_path, 'r') as f:
        content = json.load(f)
    for idx,i in enumerate(content):
        this = {
            'id': idx,
            'claim': i['question'],
            'label': i['answer']
        }
        data.append(this)
    with open('./data/Strategy_data/data_strategy.json', 'w') as f:
        json.dump(data, f, indent=4)

def read_Truthfulqa():
    path='./data/OriginalDatasets/StrategyQA/Prompt'
    content = load_from_disk(path)
    # print(content)
    claims = content['claim']
    labels = content['valid']
    data = []

    for idx,i in enumerate(content):
        # print(i)
        item = {
            'id': idx,
            'claim': i['claim'],
            'label': True if i['valid'] == 1 else False
        }
        # print(item)
        data.append(item)
        # if idx == 5:
        #     break
    # print(len(data))
    with open('./data/Strategy_data/data_Strategy_prompt.json', 'w') as f:
        json.dump(data, f, indent=4)

def read_fever():
    path = "./data/OriginalDatasets/fever_paper_test.jsonl"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    data = []
    for line in content:
        jd = json.loads(line)
        # print(jd['id'])
        if jd['verifiable'] == 'VERIFIABLE':
            label = True if jd['label'] == "SUPPORTS" else False
            claim = jd['claim']
            data.append({
                'id': jd['id'],
                'claim': claim,
                'label': label
            })
    print(len(data))
    with open('./data/fever_data/data_fever.json', 'w') as f:
        json.dump(data, f, indent=4)

def read_medqa():
    path = "./data/OriginalDatasets/dev.jsonl"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    data = []
    for idx,line in enumerate(content):
        choice = random.randint(0,1)
        dj = json.loads(line)
        label = True if choice == 0 else False
        right_answer_idx = list(dj['options'].keys()).index(dj['answer_idx'])
        answer = list(dj['options'].values())[(right_answer_idx + choice)%4]
        data.append({
            'id': idx,
            'claim':  f"{dj['question']} : {answer}",
            'label': label
        })  
    with open('./data/MedQA_data/data_medqa.json', 'w') as f:
        json.dump(data, f, indent=4)

def read_me():
    path = "./data/OriginalDatasets/me.txt"
    with open(path, 'r') as f:
        content = f.readlines()
    # print(content)
    data = []
    for idx,line in enumerate(content):
        line = line.strip()
        print(line)
        claim_content = line.split(';')[0]
        label = line.split(';')[1]
        item = {
            "id": idx,
            "claim": claim_content,
            "label": label == "True"
        }
        data.append(item)
    with open('./data/ME_data/data_me.json', 'w') as f:
        json.dump(data, f, indent=4)
        
def save_as_fromat(content, data_name):
    with open(f"./data/{data_name}_data/data_{data_name}.json", 'w') as f:
        json.dump(content, f, indent=4)
