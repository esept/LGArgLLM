import streamlit as st
from abc import ABC, abstractmethod
import json
import pandas as pd 

from ..ARTree import *

class Base_page(ABC):
    def __init__(self, name):
        st.header(f'{name}')


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
        the_index = update_option.index(update)
        # st.session_state['update_index'] = the_index
        # return the_index
        return the_index
    '''设置权重更新方法'''

    @abstractmethod
    def run(self, llm):
        raise NotImplementError

    def create_table_row(self, data, res, edges, nodes):
        """创建表格行数据"""
        return {
            'ID': data['id'],
            'LABEL': data['label'],
            'CLs': res,
            'args': [edges, nodes, data['claim']],
        }

    def read_data(self, path):
        with open(path, 'r') as f:
            data = json.loads(f.read())
        return data

    def step_tree_const(self, data, **kwargs):

        # st.markdown(update)
        # if update is None:
        #     update = st.session_state['update_index']
        rt = ART_Reasoner()
        art = ART_Tree()
        art.get_data(data)
        infos = art.update(kwargs['update'])
        # infos['this_path'] = self.this_path
        infos['this_path'] = kwargs['this_path']
        infos['llm'] = kwargs['llm']
        # st.markdown(self.llm)
        infos['id'] = kwargs['id']

        rt.begin(infos)
        result = rt.reasoning()
        return infos, result


    def save_json(self, data,path):
        try:
            json.dumps(data)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'save in {path}')
        except TypeError as e:
            print(f"数据包含不可序列化的对象: {e} {path}")
        except Exception as e:
            print(f"保存JSON文件时出错: {e} {path}")

