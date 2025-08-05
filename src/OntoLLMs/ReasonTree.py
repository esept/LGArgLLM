import os
import streamlit as st
import json
from .LLM_Managers import LLMAPI_Manager, DS_API_manager
from scipy import stats

class ReasonTree:
    def __init__(self):
        self.def_cond()
        self.S_length = 0
        self.P_length = 0  
        self.prompt_path = './configs/prompts/conds'
        self.K = 1
        self.d = 0.5

    def clean(self):
        self.S_length = 0
        self.P_length = 0
        self.confs = None
        self.judgement = None
        self.cates = None
        self.argus = None
        self.S = [None, None]
        self.P = [None, None]

    def get_attributes(self,confs, judgement, cates, argus, Id_path=[None, None]):
        self.confs = confs
        self.judgement = judgement
        self.cates = cates
        self.argus = argus
        self.id = str(Id_path[0])
        self.path = Id_path[1]
        self.split_tree()

        # self.llm = LLMAPI_Manager()
        self.llm = DS_API_manager()
        with open(os.path.join(self.prompt_path, 'base.txt'), 'r') as f:
            self.base_prompt = f.read()
             
    def set_claim(self, claim):
        self.claim = claim
    
    def get_reasoning(self, output):
        # print(output) 
        if output is not list:
            result_line = output.split('\n')
        else:
            result_line = output
        res_line = [i for i in result_line if i.startswith('Result:')]
        bool_result = res_line[0].split(': ')[1].strip().lower() == 'true'
        
        return bool_result

    def def_cond(self):
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

    def split_tree(self):
        Pw, Pu, Sw, Su = [], [], [], []
        for cate, conf, j, argu in zip(self.cates, self.confs, self.judgement, self.argus):
            if cate == 'P':
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
        # self.P_length = len(Sw) + len(Su)
        # self.S_length = len(Pw) + len(Pu)
        # self.P = [Sw, Su]
        # self.S = [Pw, Pu]

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
            
    def save_read_intersection(self, num_cond, argus):
        with open(os.path.join(self.prompt_path, f'c{num_cond}.txt'), 'r') as f:
            task = f.read()
        READ = False
        cond_dir = os.path.join(self.path, f'cond_{num_cond}')
        if not os.path.exists(cond_dir):
            os.makedirs(cond_dir)
        if self.path != None and os.path.exists(os.path.join(self.path,f'cond_{num_cond}/{self.id}.json')):
            try:
                output = self.read_file_result(self.path, num_cond)
                READ = True
            except e as Error:
                pass 
        else:
            output = self.llm.set_parameter(
                prompt = self.base_prompt + task,
                claim = self.claim,
                argus = argus
            )
            # output = self.llm.get_reasoning(self.base_prompt + task, argus) # LLM API
        if self.id != None and not READ:
            with open(f"{self.path}/cond_{num_cond}/{self.id}.json",'w') as f:
                f.write(output)
        return output 

    def logic_cond_7(self):
        num_cond = 7
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }
            output = self.save_read_intersection(num_cond, argus)
            # st.markdown('\n'.join(str(item) for item in self.P[0]))            
            # st.markdown('C7:' + output)
            return self.get_reasoning(output)
            # return True

    def logic_cond_8(self):
        num_cond = 8
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }
            output = self.save_read_intersection(num_cond, argus)
            # st.markdown('\n'.join(str(item) for item in self.P[0]))            
            # st.markdown('C8:' + output)
            return self.get_reasoning(output)

    def logic_cond_9(self):
        num_cond = 9
        if len(self.P[0]) <= 1:
            return True
        else: 
            argus = {
                'claim': self.claim,
                'P': self.P[0]
            }

            output = self.save_read_intersection(num_cond, argus)
            # st.markdown('\n'.join(str(item) for item in self.P[0]))            
            # st.markdown('C9:' + output)
            return self.get_reasoning(output)
            # return True

    def logic_cond_10(self):
        # k = st.sidebar.slider('Set k value', 1, 10, 1)  # 可自定义 k
        k = self.K
        count = sum(1 for cate, j in zip(self.cates, self.judgement) if cate == 'P' and j == 'Warranted')
        return count >= k
    

    def logic_cond_11(self):
        num_cond = 11
        if len(self.P[0]) <= 1 or len(self.S[0]) <= 1:
            return False
        argus = {
            'claim': self.claim,
            'P': self.P[0],
            'S': self.S[0]
        }
        print(f"lc11: {argus}")
        output = self.save_read_intersection(num_cond, argus)
        # # st.markdown('C11:' + output)
        return self.get_reasoning(output)
        # return False

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

    # [W,U]

    def read_file_result(self, path, num_cond):
        with open(os.path.join(path,f'cond_{num_cond}/{self.id}.json'), 'r') as f:
            data = f.read()
        if data != None:
            return data
        else:
            return False


    def reasoning(self):
        # 调用self.conditions中的函数并获取结果
        results = []
        # print(self.rc, self.all_condition)

        for i in self.rc:
            index = self.all_condition.index(i)
            condition = self.conditions[index]
            if callable(condition):  # 检查是否为可调用函数
                result = condition()  # 调用函数
            else:
                result = condition  # 直接取值
            results.append(result)

        st.markdown(results)

        st.markdown([True] * len(self.rc) == results)
        return [True] * len(self.rc) == results


    def reasoning_demo(self):
        results = []
        semantics = self.reason_with_intersection()
        res_4 = None
        res_5 = None
        res_10 = None
        for idx, i in enumerate(self.rc):
            if i in ['7', '8', '9', '11']:
                if res_4 != True and res_5 != True:
                    results.append(False)
                    continue
            index = self.all_condition.index(i)
            condition = self.conditions[index]
            if callable(condition):  # 检查是否为可调用函数
                result = condition()  # 调用函数
            else:
                result = condition  # 直接取值
            if idx == 3:
                res_4 = result
            if idx == 4:
                res_5 = result
            if idx == 9:
                res_10 = result
            results.append(result)
        return results


    def get_condition_res(self):
        results = []
        res_4 = None
        res_5 = None
        self.rc = ['1','2','3','4','5','6','7','8','9','10','11','s','p','m']

        for idx,i in enumerate(self.rc):
            if i in ['7','8','9','11']:
                if res_4 != True and res_5 != True:
                    results.append(False)
                    continue

            index = self.all_condition.index(i)
            condition = self.conditions[index]
            if callable(condition):  # 检查是否为可调用函数
                result = condition()  # 调用函数
            else:
                result = condition  # 直接取值
            if idx == 3:
                res_4 = result
            if idx == 4:
                res_5 = result
            results.append(result)
        return results

     
        
