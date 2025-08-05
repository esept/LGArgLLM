import numpy as np
import pandas as pd
import csv 

from collections import OrderedDict


class Ranker:
    def __init__(self):
        self.sources = ['MedQA_data','Strategy_data','Truth_data']
        self.read_csv()
        # self.col_conds = [f'CL_{i}' for i in range(14)]
        # self.col_sems = []

    
    def read_csv(self):
        datas = []
        for source in self.sources:
            path = f"./results/{source}.csv"
            df = pd.read_csv(path)
            datas.append(df)
        self.datas = datas
        col_names = datas[0].columns.tolist()
        self.col_Label = col_names[1]
        self.col_Conds = col_names[2:16]
        self.col_Sems = col_names[16:32]
    

    def process_condition(self):
        res = []
        for data in self.datas:
            comp_res = {}
            for col in self.col_Conds:
                if col == 'CL_10': continue # 删除无用条件
                cres = data.loc[:,self.col_Label] == data.loc[:, col]
                comp_res[col] = sum(cres)
            res.append(comp_res)
        # res = self.sum_dict(res)
        return res

    
    def process_semantic(self):
        res = []
        for data in self.datas:
            comp_res = {}
            for col in self.col_Sems:
                if col == '22': continue # 删除无用语义
                cres = data.loc[:,self.col_Label] == data.loc[:, col]
                comp_res[col] = sum(cres)
            res.append(comp_res)
        
        # res = self.sum_dict(res)
        # print(res)
        return res

    def sum_dict(self, dicts):
        return {key: sum(d[key] for d in dicts) for key in dicts[0]}

    def add_None_cond(self, conds):
        conds['CL_10'] = 0
        keys = list(conds.keys())
        index = keys.index('CL_9')
        new_keys = keys[:index + 1] + ['CL_10'] + keys[index + 1:]
        data = {key: conds[key] for key in new_keys}

        return data
    
    def add_None_sem(self, sems):
        sems['22'] = 0
        keys = list(sems.keys())
        index = keys.index('21')
        new_keys = keys[:index + 1] + ['22'] + keys[index + 1:]
        data = {key: sems[key] for key in new_keys}
        
        return data

    def rank_pbw(self, data):
        sorted_desc = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        # print(len(data))

        # for i,j in enumerate(sorted_desc):
        #     print(i,sorted_desc[j],j)
        # print('--'*20)


        max_value = max(sorted_desc.values())
        if max_value > 300:
            length = 300
        else:
            length = 100
        # print(sorted_desc)
        this_values = data.copy()
        values = [sorted_desc[key] for key in list(sorted_desc.keys()) if sorted_desc[key] > length]
        
        for k in sorted_desc:
            # values.copy()
            v = sorted_desc[k]
            if v < length:
                this_values[k] = 0
                continue
            down = len([i for i in values if v > i])
            inc = values.count(v) - 1
            this_values[k] = 2 * down + inc
            # print(f"{2 * down + inc} === inc= {inc} + 2 * down = {down}")
        # for i,j in enumerate(this_values):
        #     print(i,this_values[j],j)
        # print('==='*20)
        return this_values

    def rank_borda(self, data):
        sorted_desc = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        max_value = max(sorted_desc.values())

        if max_value > 300:
            length = 300
        else:
            length = 100
        this_values = data.copy()

        values = [sorted_desc[key] for key in list(sorted_desc.keys()) if sorted_desc[key] > length]
        max_score = len(values)
        prev_v = -1
        for k in sorted_desc:
            v = this_values[k]
            if v < length:
                this_values[k] = 0
                continue
            if prev_v == v :
                this_values[k] = this_score
                print(this_score)
                continue
            inc = values.count(v)
            this_values[k] = max_score
            this_score = np.mean([max_score - i for i in range(inc)])
            this_values[k] = this_score
            prev_v = v
            print(this_score)
            max_score -= inc
        print(this_values)
        return this_values


    def calcul_cond_weight(self, cond_dict):
        semantics = {
            '15': [0,1,3],
            '16': [0,2,3],
            '17a': [2,3,4],
            '17e': [1,3,4],
            '18': [1,3,4,5],
            '19': [3,4,6],
            '20': [3,4,7], 
            '21': [3,4,8],
            '22': [3,4,9,10],
            's': [3,11],
            'p': [3,12],
            'm': [3,13],
            'sp': [3,11,12],
            'sm': [3,11,13],
            'pm': [3, 12, 13],
            'spm': [3,11,12,13]
        }
        # print(cond_dict)
        ll = []
        for sem in semantics:
            value = semantics[sem]
            this_weight = [cond_dict[f'CL_{v}'] for v in value]
            this_weight = [i/sum(this_weight) for i in this_weight]
            # print(this_weight,',')
            ll.append(this_weight)
        return ll

            
    def calcul_sem_weight(self, sem_dict):
        # print(sem_dict)
        values = list(sem_dict.values())
        # print(values)
        ll = [v/sum(values) for v in values]
        return ll