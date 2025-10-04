import os

import pandas as pd
import numpy as np


class Ranker:
    def __init__(self):
        self.dc = [] # 正确个数 Cond
        self.ds = [] # 正确个数 Cond
        self.ws = [] # sem 权重
        self.wc = [] # cond 权重
        self.path = "./result"
        self.read_files()


    def read_files(self):
        all_files = os.listdir(self.path)
        csvs = [i for i in all_files if i.endswith('csv')]
        for csv in csvs:
            self.analyse_result(csv)

    def analyse_result(self, file_name):
        # print(file_name)
        full_path = os.path.join(self.path, file_name)
        df = pd.read_csv(full_path)

        conds = ['1_cond', '2_cond', '3_cond', '4_cond', '5_cond',
       '6_cond', '7_cond', '8_cond', '9_cond', '10_cond', '11_cond', 's_cond',
       'p_cond', 'm_cond']
       #  sems = ['15', '16', '17a', '17e', '18', '19', '20',
       # '21', '22', 's', 'p', 'm', 'sp', 'sm', 'pm', 'spm']
        sems = ['15', '16', '17a', '17e', '18', '19', '20',
                '21', 's', 'p', 'm', 'sp', 'sm', 'pm', 'spm']

        conds_results = self.compare_and_sum(df, conds, target_column='label')
        sems_results = self.compare_and_sum(df, sems, target_column='label')
        # self.rank_borda(conds_results)
        self.dc.append(conds_results)
        self.ds.append(sems_results)

        self.ws.append(self.rank_borda(sems_results))
        # self.ws.append(self.rank_pbw(sems_results))
        self.wc.append(self.rank_pbw(conds_results))
        # self.wc.append(self.rank_borda(conds_results))



    def collect_weights(self, data):
        weights = data[0]
        for file in data[1:]:
            for key in weights:
                weights[key] += file[key]
        # print(weights)
        return weights



    def sort_dict(self, the_dict):
        sort_ = sorted(
            the_dict.items(),
            key=lambda item: item[1],
            reverse=True
        )
        return sort_

    def compare_and_sum(self, dataframe, column_list, target_column='label'):
        result_dict = {}
        for col in column_list:
            match_count = (dataframe[col] == dataframe[target_column]).sum()
            result_dict[col] = int(match_count)
        return result_dict

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
                continue
            inc = values.count(v)
            this_values[k] = max_score
            this_score = np.mean([max_score - i for i in range(inc)])
            this_values[k] = this_score
            prev_v = v
            max_score -= inc
        # print(f'borda = {this_values}')
        return this_values

    def rank_pbw(self, data):
        sorted_desc = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

        max_value = max(sorted_desc.values())
        if max_value > 300:
            length = 300
        else:
            length = 100
        this_values = data.copy()
        values = [sorted_desc[key] for key in list(sorted_desc.keys()) if sorted_desc[key] > length]

        for k in sorted_desc:
            v = sorted_desc[k]
            if v < length:
                this_values[k] = 0
                continue
            down = len([i for i in values if v > i])
            inc = values.count(v) - 1
            this_values[k] = 2 * down + inc
        # print(f'pbw = {this_values}')
        return this_values
