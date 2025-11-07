import os 
import json
from fcntl import FASYNC

from scipy import stats
import streamlit as st
from ..LLM_Manager import *

"""Hyper Parameter"""
KK = 1
DD = 0.5
"""Hyper Parameter"""

class ART_Reasoner:
    '''--------------------------<Setup>--------------------------'''
    def __init__(self):
        self.prompt_path = "./configs/prompts/conds"
        self.llm_reason = ["7","8","9","11"]
        self.K = KK
        self.d = DD
        self.rc = ['1','2','3','4','5','6','7','8','9','10','11','s','p','m']
        self.define_conditions()
        self._clean()
        self.read_cond_prompt()

        
    def read_cond_prompt(self):
        with open(os.path.join(self.prompt_path,'base.txt'), 'r') as f :
            self.base_prompt = f.read()
        self.conds_prompt = {}
        for num in self.llm_reason:
            with open(os.path.join(self.prompt_path, f'c{str(num)}.txt'), 'r') as f:
                self.conds_prompt[num] = f.read()

    def _clean(self):
        self.S_length = 0
        self.P_length = 0
        self.confs = None
        self.judgement = None
        self.cates = None
        self.argus = None
        self.S = [None, None]
        self.P = [None, None]

    def begin(self, info):
        self.data = info
        self.id = info['id']
        self.llm = info['llm']
        self.claim = info['root'].get_argu()
        # st.markdown(self.claim)
        self.split_trees()
        # print(self.data['this_path'])
        if str(self.data['this_path']).endswith('json'):
            stock_path = "/".join(self.data["this_path"].split('/')[:-1])
        else:
            stock_path = self.data["this_path"]
        self.st_path = stock_path
        for num in self.llm_reason:
            the_path = os.path.join(stock_path,f"cond_{num}")
            if not os.path.exists(the_path):
                # print(the_path)
                os.makedirs(the_path)

    '''--------------------------<Logic Conditions>--------------------------'''

    def split_trees(self):
        Pw, Pu, Sw, Su = [], [], [], []
        for node, j in zip(self.data['trees'], self.data['judge']):
            gnode = node[0].get_node()
            conf = gnode['newconf']
            cate = gnode['cate']
            argu = gnode['text']
            if cate == "P":
                if j == 'Warranted':
                    Pw.append((conf, j, argu))
                elif j == 'Unwarranted':
                    Pu.append((conf, j, argu))
            elif cate == 'S':
                if j == 'Warranted':
                    Sw.append((conf, j, argu))
                elif j == 'Unwarranted':
                    Su.append((conf, j, argu))
        self.S_length = len(Sw) + len(Su)
        self.P_length = len(Pw) + len(Pu)
        self.S = [Sw, Su]
        self.P = [Pw, Pu]

    def reasoning(self):
        results = {i:None for i in self.rc}
        res_4 = None
        res_5 = None
        for idx, r_num in enumerate(self.rc):
            # print(idx, r_num)
            if r_num in self.llm_reason:

                if res_4 != True and res_5 != True:
                    results[r_num] = False
                    # condition = self.conditions[idx]
                # results[r_num] = condition()
                else:
                    condition = self.conditions[idx]
                    # print(r_num)
                    results[r_num] = condition()
                continue

            condition = self.conditions[idx]
            result = condition()
            results[r_num] = result
            if idx == 3:
                res_4 = result
            if idx == 4:
                res_5 = result
        return results
    '''--------------------------<Logic Conditions>--------------------------'''
    def verifier_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def reason_by_llm(self, num_cond, argus):
        READ = False
        the_path = os.path.join(self.st_path,f"cond_{num_cond}/{self.data['id']}.json")
        # print(the_path)
        if os.path.exists(the_path):
            try:
                output = self.read_file_result(the_path)
                READ = True
            except Exception as Error:
                # print(f"Error reading cache {the_path}, will regenerate. Error: {Error}")
                # READ = False  # 强制重新生成
                raise Error
        else:
            output = self.llm.get_condtion_parameter(
                prompt = self.base_prompt + self.conds_prompt[num_cond],
                claim = self.claim,
                argus = argus
            )
        if self.id != None and not READ:
            with open(the_path, 'w') as f:
                f.write(output)
        return output

    def read_file_result(self, the_path):
        with open(the_path, 'r') as f:
            data = f.read()
        if data != None:
            return data
        else:
            return False

    def get_reasoning(self, output):
        # print(output)
        if output is not list:
            result_line = output.split('\n')
        else:
            result_line = output
        res_line = [i for i in result_line if i.startswith('Result:')]
        # print(res_line[0])
        bool_result = res_line[0].split(': ')[1].strip().lower() == 'true'

        return bool_result

    '''--------------------------<Logic Conditions>--------------------------'''

    def define_conditions(self):
        self.conditions = [
            self.logic_cond_1,
            self.logic_cond_2,
            self.logic_cond_3,
            self.logic_cond_4,
            self.logic_cond_5,
            self.logic_cond_6,
            self.logic_cond_7,
            self.logic_cond_8,
            self.logic_cond_9,
            self.logic_cond_10,
            self.logic_cond_11,
            self.logic_cond_s,
            self.logic_cond_p,
            self.logic_cond_m,
        ]
        self.all_condition = [(i.__name__).split('_')[-1] for i in self.conditions]

    def logic_cond_1(self):
        ''' P != ∅ and S == ∅. '''
        # print(f'aP = {self.P_length}     S = {self.S_length}')
        return self.P_length != 0 and self.S_length == 0

    def logic_cond_2(self):
        '''∃ T ∈ P, Judge(T ) = (W arranted, ω).'''
        return self.P_length != 0 and len(self.P[0]) != 0

    def logic_cond_3(self):
        ''' ∀ T ∈ P, Judge(T) = (Warranted, ω) and P != ∅. ''' # 所有的 P 都是 warranted, 同时 P 的个数 > 0
        return self.P_length > 0 and len(self.P[1]) == 0 
            
    def logic_cond_4(self):
        '''maxT ∈P {ω | Judge(T) = (Warranted, ω)} ≥ d, d ∈ [0, 1].'''
        # d = st.sidebar.slider('Set d value', 0.0, 1.0, 0.5)
        d = self.d
        if len(self.P[0]) == 0:
            return False
        return max([i for i, _, _ in self.P[0]]) >= d

    def logic_cond_5(self):
        '''所有的 S 都是 Su'''
        return len(self.S[0]) == 0
            
    def logic_cond_6(self):
        return len(self.P[1]) == 0
        
    def logic_cond_7(self):
        num_cond = "7"
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }
            output = self.reason_by_llm(num_cond, argus)
            return self.get_reasoning(output)

    def logic_cond_8(self):
        num_cond = "8"
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }
            output = self.reason_by_llm(num_cond, argus)
            return self.get_reasoning(output)

    def logic_cond_9(self):
        num_cond = "9"
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }
            output = self.reason_by_llm(num_cond, argus)
            return self.get_reasoning(output)
            # return True

    def logic_cond_10(self):
        k = self.K
        cates = [tree[0].cate for tree in self.data['trees']]
        count = sum(1 for cate, j in zip(cates, self.data['judge']) if cate == 'P' and j == 'Warranted')
        return count >= k

    def logic_cond_11(self):
        num_cond = "11"
        if len(self.P[0]) <= 1 or len(self.S[0]) <= 1:
            return False
        argus = {
            'claim': self.claim,
            'P': self.P[0],
            'S': self.S[0]
        }
        output = self.reason_by_llm(num_cond, argus)

        return self.get_reasoning(output)

    def logic_cond_s(self):
        # |T∈S,Judge(T)=(Warranted,ω)|≤|T′∈S,Judge(T′)!=(Warranted,ω′)|.
        if len(self.S[0]) <= len(self.S[1]):
            return True
        return False

    def logic_cond_p(self):
        # |T∈P,Judge(T)=(Warranted,ω)| ≥ |T′∈P,Judge(T′)!=(Warranted,ω′)|.
        if len(self.P[0]) >= len(self.P[1]):
            return True
        return False

    def logic_cond_m(self):
        # |T∈P,Judge(T) = (Warranted, ω)|≥|T′∈S,Judge(T′)=(Warranted,ω′)|.
        if len(self.P[0]) >= len(self.S[0]):
            return True
        return False
