import pandas as pd
import numpy as np
import os
import json

Reasoning = ['15', '16', '17a', '17e', '18', '19', '20', '21', '22', 's', 'p', 'm', 'sp', 'sm', 'pm', 'spm', 'threshold_True', 'wcon_sem', 'wcon_wsem']



def read_argllms():
    path = './results/argllms'
    sources = ['medqa','strategyQA','truthfulQA']
    datas = []
    
    for idx, source in enumerate(sources):
        full_path = os.path.join(path, f'{source}.jsonl')
        this_source = []

        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                if 'id' in data and 'is_correct' in data:
                    item = {
                        'id': data['id'],
                        'is_correct': data['is_correct']
                    }
                    this_source.append(item)
        datas.append(this_source)
    
    return datas


def read_ontollm(num=0):
    sources = ['MedQA','Strategy','Truth']
    path = "./results/"
    all_data = []
    for source in sources:
        source_data = []
        full_path = os.path.join(path, f'{source}_data.csv')
        df = pd.read_csv(full_path)
        col_names = df.columns.tolist()
        if len(col_names) > 16:
            col_Reasoning = col_names[16:]
            choice = col_Reasoning[num]
            cols = ['ID','LABEL'] + [choice]
            missing_cols = [col for col in cols if col not in col_names]
            df = df.loc[:, cols]
            for index, row in df.iterrows():
                item = {
                    'ID': row['ID'],
                    'LABEL': row['LABEL'],
                    'choice': row[choice]
                }
                source_data.append(item)
            
            all_data.append(source_data)
    return all_data
        
def compare(args, ontos,after=100):
    for arg, onto in zip(args, ontos):
        count_arg = 0
        count_onto = 0
        for idx, line in enumerate(arg):
            if line['is_correct']:
                count_arg += 1
            onto_line = onto[idx]
            if onto_line['LABEL'] == onto_line['choice']:
                count_onto += 1
            if idx > after:
                if count_arg > count_onto:
                    break
                # if count_arg < count_onto:
                #     break
        print(idx, count_arg,count_onto)
# 0 15
# 1 16
# 2 17a
# 3 17e
# 4 18
# 5 19
# 6 20
# 7 21
# 8 22
# 9 s
# 10 p
# 11 m
# 12 sp
# 13 sm
# 14 pm
# 15 spm
# 16 threshold_True
# 17 wcon_sem
# 18 wcon_wsem

# 测试函数
if __name__ == '__main__':
    arg_data = read_argllms()
    tt = [i for i in range(19)]
    # tt = []
    for i in tt:
        print(f'-----{i}-----')
        onto_data = read_ontollm(i)
        compare(arg_data, onto_data,after=0)
