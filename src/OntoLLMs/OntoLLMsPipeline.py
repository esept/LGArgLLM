import os
import json 
import streamlit as st
from datasets import load_from_disk
import pandas as pd
import numpy as np


import threading # 多线程
from concurrent.futures import ThreadPoolExecutor

from .ReasonTree import ReasonTree
from .Argument_Generator import Argument_Generator
from .VisTree import VisTree
from .AttackTree import *
from .Reasoning import Reasoning
from .Ranker import Ranker

class OntoLLMsPipeline:
    def __init__(self):
        self.model = "Pro/deepseek-ai/DeepSeek-V3"
        self.DEMO_PATH = "./data/Truth_data/dpsk_Tests"
        self.NB_Semantics = 16

    def read_list_llms(self):
        with open('./configs/llms.conf', 'r') as f:
            llms = f.readlines()
        llms = [llm.strip() for llm in llms]
        return llms

    def set_update(self):
        st.sidebar.header('Set Update choice')
        update_option = [
            'tanh(nb_CA - nb_CR)',
            '- MAX (CA - CR)',
            'MAX(CA) - MAX(CR)',
            'tanh(SUM(CA)-SUM(CR))',
            'split(nb_CA/nb_C)',
            '-1',
            'ATTACK_relation'
        ]
        update = st.sidebar.radio(
            'select how to update score',
            options=update_option,
            index=2
        )
        return update_option.index(update)
    '''设置权重更新方法'''

    def read_datasets(self, path='./data'):
        data_list = []
        for i in os.listdir(path):
            if i.endswith('_data'):
                the_dir_path = os.path.join(path,i)
                for subdir in os.listdir(the_dir_path):
                    
                    if subdir.endswith('json'):
                        data_list.append(os.path.join(the_dir_path, subdir))
        return data_list
    '''读取所有可以被可视化的数据集路径'''

    def set_dataset_model(self):
        all_datas = self.read_datasets()
        all_data_display = [i.split('/')[-1] for i in all_datas]
        datachoice = st.sidebar.radio(
            'select datasets',
            options=all_data_display,
            index=0
        )
        return all_datas[all_data_display.index(datachoice)]
    '''选择要可视化的数据'''

    def read_data(self, dataset_path):
        with open(dataset_path, 'r') as f:
            data = json.loads(f.read())
        self._data = data

    def process_demo_claims(self,data):
        claims = {}
        for json_f in data:
            claims[str(json_f['id']) + ' - ' + json_f['claim']] = os.path.join(self.DEMO_PATH, f'{json_f["id"]}.json')
            # claims[str(idx) +" - "+ data['claim']] = os.path.join(self.DEMO_PATH, json_f)
        return claims, data
    '''读取所有demo中的数据'''

    def save_json(self, data, path):
        try:
            json.dumps(data)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'save in {path}')
        except TypeError as e:
            print(f"数据包含不可序列化的对象: {e}")
        except Exception as e:
            print(f"保存JSON文件时出错: {e}")
    """保存 json 到本地"""

    def visualize_data(self, vt, edges, nodes, claim):
        st.header(claim)
        # vt.draw_first_tree(fedge, fnode, at.judgement, claim_res)
        vt.get_data(edges, nodes)
        if st.sidebar.button('back to table'):
            st.rerun()
    '''展示攻击森林结构'''

    def setup_streamlit(self):
        st.set_page_config(layout="wide")

    def initialize_data(self):
        this_data = self.set_dataset_model()
        this_update = self.set_update()
        st.header(this_data)
        self.read_data(this_data)
        return this_data, this_update

    def prepare_evaluation_data(self, this_data):
        repo_json = os.path.join('/'.join(this_data.split('/')[:-1]), 'dpsk_Tests')
        ids = sorted([i.split('.')[0] for i in os.listdir(repo_json) if i.endswith('json')])
        all_ids = [str(i['id']) for i in self._data[0:200]]
        ext_id = [all_ids.index(i) for i in ids]
        datas = []
        for i in ext_id:
            data = {
                'id': self._data[i]['id'],
                'label': self._data[i]['label'],
                'claim': self._data[i]['claim'],
                'jpath': os.path.join(repo_json, str(self._data[i]['id']) + '.json')
            }
            datas.append(data)
        return sorted(datas, key=lambda x: int(x['id'])), repo_json

    def process_single_data(self, data, at, rt, this_update):
        # try: 
        with open(data['jpath'], 'r') as f:
            content = f.read()
        json_data = json.loads(content)

        # 攻击树
        at.get_data(data['claim'], json_data, this_update)
        nodes = at.nodes
        at.update()
        fedge, fnode, fargus = at.get_first_tree()
        node_cate = [n['cate'] for n in fnode][1:]
        final_conf = fnode[0]['newconf']

        # 推理树
        repo_json = '/'.join(data['jpath'].split('/')[:-1])
        rt.set_claim(data['claim'])
        rt.get_attributes(at._conf_supps, at.judgement, node_cate, fargus, [data['id'], repo_json])

        conds = rt.get_condition_res()

        return conds, at.edges, at.nodes, final_conf

    def create_table_row(self, data, res, edges, nodes):
        """创建表格行数据"""
        return {
            'ID': data['id'],
            'LABEL': data['label'],
            'CLs': res,
            'args': [edges, nodes, data['claim']],
        }

    def run_ranker(self):
        rk = Ranker()
        cond_res = rk.process_condition()
        sem_res = rk.process_semantic()

        rr = []
        for r in cond_res:
            cond_rk_pbw = rk.rank_pbw(r)
            cond_rk_pbw = rk.add_None_cond(cond_rk_pbw)
            rr.append(cond_rk_pbw)
        rr = rk.sum_dict(rr)
        cond_weight = rk.calcul_cond_weight(rr)

        rs = []
        for s in sem_res:
            sem_rk_pbw = rk.rank_pbw(s)
            sem_rk_pbw = rk.add_None_sem(sem_rk_pbw)
            rs.append(sem_rk_pbw)
        ss = rk.sum_dict(rs)
        # print(ss)

        sem_weight = rk.calcul_sem_weight(ss)
        return cond_weight, sem_weight



    def evaluate_s(self):
        this_data, this_update = self.initialize_data()
        # print(this_update)
        datas, repo_json = self.prepare_evaluation_data(this_data)
        
        data_name = repo_json.split('/')[-2]
        at = AttackTree()
        rt = ReasonTree()
        vt = VisTree()

        table_data = []
        for data in datas: 
            # print(data)
            # break
            res, edges, nodes, tree_conf = self.process_single_data(data, at, rt, this_update)

            if res is not None:
                table_row = self.create_table_row(data, res, edges, nodes)
                table_data.append(table_row)

            rt.clean()
            at.clean()




        ag = Reasoning(self.NB_Semantics, table_data, name=data_name)
        

        cond_weight, sem_weight = self.run_ranker()
        ag.set_condition_weight(cond_weight)
        ag.set_semantic_weight(sem_weight)

        ag.add_col(ag.threshold_True)
        ag.add_col(ag.wcon_sem)
        ag.add_col(ag.wcon_wsem)
        ag.add_col(ag.veto, veto_N=5)

        ag.display_default(['veto','threshold_True','wcon_sem','wcon_wsem'])

        print('----' * 20)

    def demo(self):
        # st.set_page_config(layout='wide')
        folder_path = self.DEMO_PATH.split('/')
        # print
        folder_path = '/'.join(folder_path[:3]) + '/'
        org_path = [os.path.join(folder_path,i) for i in os.listdir(folder_path) if i.endswith('json')][0]
        self.read_data(org_path)

        data = self.prepare_evaluation_data(org_path)
        # print(data[0][0])

        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
            st.session_state.json_data = None
            st.session_state.claim_text = ''

        if 'reasoning_updated' not in st.session_state:
            st.session_state.reasoning_updated = False

        claim_list, data = self.process_demo_claims(data[0])
        rt = ReasonTree()
        at = AttackTree()
        vt = VisTree()
        choice = st.selectbox('Exist Claims', claim_list.keys(), index=2)
        update_way = self.set_update()
    
        this_idx = int(choice.split('-')[0].strip())
        this_data = data[this_idx]

        st.session_state.claim_text = choice
 
        res, edges, nodes, tree_conf = self.process_single_data(this_data, at, rt, update_way)
        
        table_row = self.create_table_row(this_data, res, edges, nodes)
        ag = Reasoning(self.NB_Semantics, [table_row], name='demo')
        conditions_res = rt.get_condition_res()
        claim_res = ag.reason_semantics(conditions_res)
        claim_res['Label'] = this_data['label']


        fedge, fnode, fargus = at.get_first_tree()

        conditions_df = pd.DataFrame([conditions_res])
        # conditions_df.columns = ['Result']
        st.dataframe(conditions_df)

        claim_df = pd.DataFrame([claim_res])

        # claim_df.columns = ['Result']
        st.dataframe(claim_df)


        vt.draw_first_tree(fedge, fnode, at.judgement, claim_res)
        vt.get_data(at.edges, nodes)
        print('---')
    '''演示树形结构'''
    
    def chercher_rest(self, data, spath):
        spath = os.path.join(spath, 'dpsk_Tests')
        jfiles = [int(file.split('.')[0]) for file in os.listdir(spath) if file.endswith('json')]
        rest = []
        # print(f"{len(jfiles)}")
        for i in data:
            if i['id'] not in jfiles:
                rest.append(i['id'])

        # print(len(rest))
        return rest


    def run_with_new_data(self, path):
        self.read_data(path)

        storage_path = "/".join(path.split("/")[:3])

        def process_item(i, idx, model):
            ag = Argument_Generator(model)
            this_id = i['id']
            print(f"{i['id']}\t{i['label']}")
            this_claim = i['claim']
            ag.set_claim(this_claim)

            data = ag.generate_AttackData()
            json_path = f'{storage_path}/dpsk_Tests/{this_id}.json'
            self.save_json(data, json_path)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            for idx, i in enumerate(self._data[87:113]):
                idx += 1
                futures.append(executor.submit(
                    process_item, 
                    i, 
                    idx,
                    self.model  # 传递模型参数而非实例
                ))
            
            for future in futures:
                future.result()

        # pass
    '''使用新数据进行测试'''

    def runner(self, mode='EVA', **kwargs):
        self.setup_streamlit()
        if mode == 'EVA': # evaluate
            print('eva')
            self.evaluate_s()
        elif mode == 'ND': # new Dataset
            print(f"Running with new Datasets {kwargs.get('data_path')}")
            self.run_with_new_data(kwargs.get("data_path"))
            # self.evaluate_p()
        else:
            self.demo() # 演示结构

