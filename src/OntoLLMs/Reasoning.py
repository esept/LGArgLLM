import numpy as np
import pandas as pd

import scipy 
import streamlit as st
from .Ranker import Ranker


class Reasoning:
    def __init__(self, NB_Semantics ,data, name):
        self.name = name
        self.nb = NB_Semantics
        self.data = data
        self.add_semantics_res()
        self.rk = Ranker()

    def set_semantic_weight(self, weight):
        self.semantic_weight = weight
    
    def set_condition_weight(self, weight):
        self.condition_weight = weight

    def add_semantics_res(self):
        for row in self.data:
            sems_res = self.reason_semantics(row['CLs'])
            row['semantics_results'] = sems_res
        self.sems_cols = list(sems_res.keys())
        # print(self.data)

    def give_icon_res(self,bool_val):
        if bool_val:
            return '✅'
        return '❌'

    def save_csv(self,name, other=[]):
        csvs = []
        for row in self.data:
            csv_row = {
                'ID': row['ID'],
                'LABEL': int(row['LABEL']),
                **{f'CL_{i}': int(res) for i, res in enumerate(row['CLs'])},
                # 'CLs': '|'.join([r for r in row['CLs']]),
                **{sem: int(row['semantics_results'][sem]) for sem in self.sems_cols},
                # **{i: int(row[i]) for i in other}
            }
            csvs.append(csv_row)
        # print(csvs) 
        result = pd.DataFrame(csvs)
        result.to_csv(f'./results/{name}.csv', index=False)
        print(f"Result SAVE TO ./results/{name}.csv")
        
        

    def display_default(self, other=[]):
        display_data = []
        default_cols = ['LABEL'] + other

        for row in self.data:

            display_row = {
                'ID': row['ID'],
                'LABEL': self.give_icon_res(row['LABEL']),
                'CLs': '|'.join([self.give_icon_res(r) for r in row['CLs']]),
                **{sem: self.give_icon_res(row['semantics_results'][sem]) for sem in self.sems_cols},
                **{i: self.give_icon_res(row[i]) for i in other}
            }
            display_data.append(display_row)

        df = pd.DataFrame(display_data)

        def highlight_matching_cells(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            
            for idx in df.index:
                label_value = df.loc[idx, 'LABEL']
                
                for semantic_col in self.sems_cols + other:
                    if semantic_col in df.columns:
                        semantic_value = df.loc[idx, semantic_col]
                        
                        if semantic_value == label_value:
                            styles.loc[idx, semantic_col] = 'background-color: lightblue; font-weight: bold'
            
            return styles
        
        styled_df = df.style.apply(highlight_matching_cells, axis=None)
        total_samples = len(self.data)
        st.dataframe(styled_df, use_container_width=True)
        total_correct = self.calcul_acc(display_data, self.sems_cols + other)
        columns = self.sems_cols + other



        accuracy_data = {
            'Nom': columns,
            'Total Correct': total_correct,
            'Acc': [f'{correct/total_samples:.2%}' for correct in total_correct]
        }
        accuracy_df = pd.DataFrame(accuracy_data)
        accuracy_df = accuracy_df.astype(str).T
        st.dataframe(accuracy_df, use_container_width=True)

        
    def reason_semantics(self, conditions):
        semantics_res = {}

        semantics = self.get_semantics()
        for idx, sem in enumerate(semantics):
            val = semantics[sem]
            res = [conditions[i] for i in val]
            semantics_res[sem] = all(res)

        return semantics_res
  
    def get_poids(self, conds, res):
        weight_semantics = self.condition_weight

        pps = []

        for i, j in enumerate(weight_semantics[conds]):
            pps.append( j * res[i] )

        return sum(pps)


    def calcul_acc(self, data, cols):
        numbers = [0 for i in range(len(cols))]
        for line in data: 
            Correct = line['LABEL']
            for idx,n in enumerate(cols): # 17
                numbers[idx] += int(Correct == line[n])
        return numbers

    def add_col(self, function_name, *args, **kwargs):
        print(f'ADDING COL {function_name.__name__}')
        valeurs = function_name(*args, **kwargs)
        for i, line in enumerate(self.data):
            line[function_name.__name__] = valeurs[i]
        
    def get_semantics(self):
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
        return semantics

    def wcon_wsem(self):
        '''
        weight_condition - semantic
        '''
        semantics = self.get_semantics()

        weights = self.semantic_weight
        values = []
        for line in self.data:
            thisLine = line['CLs']
            # print(thisLine)
            this_weights = []
            for idx, sem in enumerate(semantics):
                val = semantics[sem]
                res = [thisLine[i] for i in val]
                this_weights.append(self.get_poids(idx, res) * weights[idx])
            values.append(sum(this_weights))
        # print(values)
        return values >= np.median(values)
    # weight_condition - semantic

    def save_digit_semantic(self, data, name):
        ids = [line.get('ID', '') for line in self.data]
        labels = [line.get('LABEL', '') for line in self.data]

        cols = ['15','16','17a','17e','18','19','20','21','22','s','p','m','sp','sm','pm','spm']
        
        new_cols = ['ID', 'LABEL'] + cols
        
        data.insert(0, new_cols)
        
        for i in range(1, len(data)):
            if i-1 < len(ids) and i-1 < len(labels):
                data[i] = [ids[i-1], labels[i-1]] + data[i]
            else:
                data[i] = ['', ''] + data[i] 
        
        df = pd.DataFrame(data[1:], columns=data[0])
        
        df.to_csv(f"./results/{name}_digit_sem.csv", index=False, float_format='%.2f')
    # save digit weight_condition - semantic results
        
    def wcon_sem(self):
        '''
        weighted_condition - weighted_semantic
        '''
        
        semantics = self.get_semantics()
        values = []
        sem_values = []
        for line in self.data:
            thisLine = line['CLs']
            # print(thisLine)
            this_weights = []
            # 
            for idx, sem in enumerate(semantics):

                val = semantics[sem]
                res = [thisLine[i] for i in val]
                this_sem_poid = self.get_poids(idx, res)
                this_weights.append( this_sem_poid)
                # sem_values = this_sem_poid
            # print(this_weights
            values.append(sum(this_weights))
            sem_values.append(this_weights)
        name = self.name
        self.save_digit_semantic(sem_values, name=name)
        
        return values >= np.median(values)
    # weighted_condition - weighted_semantic
            
    def threshold_True(self, threshold=0.55):
        '''
        V_True > V_False
        '''
        values = []
        for line in self.data:
            thisLine = list(line['semantics_results'].values())
            thisLine.remove(thisLine[8])
            cTrue = thisLine.count(True) / len(thisLine)
            # cFalse = thisLine.count(False)
            values.append(cTrue >= threshold)
        return values

    def veto(self,veto_N=5):
        '''
        remove the N worst in list
        '''
        
        values = []
        weights = self.semantic_weight
        keys = list(self.data[0]['semantics_results'].keys())
        
        dict_weights = {i:j for i,j in zip(keys, weights)}
        sorted_dweights = dict(sorted(dict_weights.items(), key=lambda x:x[1], reverse=True))
        sorted_keys = list(sorted_dweights.keys())[veto_N:]


        values = []
        for line in self.data:
            thisLine = line['semantics_results']
            veto_True = sum([1 for k in sorted_keys if thisLine[k] == True])
            values.append(veto_True >= (len(keys) - veto_N)/2)
        return values

