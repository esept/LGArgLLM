import concurrent.futures
import os
from .Base_page import Base_page
import streamlit as st
import pandas as pd
import time

from ..Evaluator import Evaluator
from ..Reasoner import Reasoner
from ..Ranker import Ranker

import threading # 多线程
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 8

class Page_Evaluation(Base_page):
    def __init__(self):
        super().__init__("Evaluation")

    def get_list_dataset(self):
        data_path = "./data"
        data_list = {i: os.path.join(data_path,i) for i in os.listdir(data_path) if os.path.isdir(os.path.join(data_path,i)) and i != 'ELSE'}
        # st.markdown(data_list)
        names = list(data_list.keys())
        st.sidebar.header('Set Dataset')
        dataset = st.sidebar.radio(
            'select dataset to evaluate',
            options=names
        )
        return data_list[dataset]

    def read_full_dataset(self, path):
        folder_l = [int(f.split('_')[-1]) for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]
        the_num = max(folder_l)
        folder = os.path.join(path, f'res_{the_num}')
        st.markdown(f'Reading **{folder}** ...')
        all_datas = {}
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            num = file_path.split('/')[-1].split('.')[0]
            # st.markdown(num)
            if not file_path.endswith('json'):
                continue
            this_data = super().read_data(file_path)
            all_datas[num] = this_data
        return all_datas, folder

    def process_dataset_item(self,num_str, label_val, data_val,folder_path_val, update_val):
        num = int(num_str)

        label = {'label':True} if label_val else {'label':False}
        info, result = super().step_tree_const(
            data_val,
            this_path=os.path.join(folder_path_val, f'{num_str}.json'),
            llm=self.llm,
            id=num_str,
            update=update_val
        )
        list_result = list(result.values())
        list_result.append(label)

        return {
            'label': label_val,
            'num': num,
            'info': info,
            'result': result,
        }


    def run(self, llm):
        the_dataset = self.get_list_dataset()
        self.llm = llm
        labels = self.read_labels(the_dataset)
        datasets, folder_path = self.read_full_dataset(the_dataset)
        # print(datasets)
        update = super().set_update()
        all_results = {}
        all_infos = {}
        all_cond_res = {}
        reasoner = Reasoner()
        start_time = time.time()
        dict_labels = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []

            for num_int in range(len(datasets)):
                num_str = str(num_int)

                label_val = labels[num_str]
                # print(label_val)
                # dict_labels[int(num_str)] = label_val
                data_val = datasets[num_str]

                future = executor.submit(
                    self.process_dataset_item,
                    num_str,
                    label_val,
                    data_val,
                    folder_path,  # 假设 folder_path 不变
                    update,  # 假设 update 不变

                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    num = res['num']
                    dict_labels[num] = res['label']
                    all_infos[num] = res['info']
                    all_cond_res[num] = res['result']
                except Exception as exc:
                    print(f'Error in {exc}')
        df_conds = pd.DataFrame(all_cond_res).T
        reasoner.get_data(df_conds)
        '''------------ <Add Aggregation> ------------'''
        reasoner.add_reasoner(reasoner.agg_threshold_True)
        reasoner.add_reasoner(reasoner.agg_veto)

        # reasoner.get_label(dict_labels)


        reasoner.add_reasoner(reasoner.agg_Wc_S)
        reasoner.add_reasoner(reasoner.agg_Wc_Ws)

        dict_sems = reasoner.get_results()
        end_time = time.time()
        # st.markdown(f'Running Time: {end_time - start_time}')



        label_series = pd.Series(dict_labels)
        dict_sems['label'] = label_series

        # reasoner

        self.display_evaluation(df_conds, dict_sems, folder_path)

    def display_evaluation(self, res_cond,res_sems, path):
        eva = Evaluator(res_sems)
        df_cond_res = res_cond.add_suffix('_cond')
        # df_all = pd.concat((df_cond_res, res_sems), axis=1).sort_index()
        df_all = pd.concat((df_cond_res, res_sems), axis=1)
        st.dataframe(df_all)
        dataset_name = path.split('/')[-2]
        if st.button('SAVE RESULT'):
            save_path = os.path.join('./result/', f'{dataset_name}.csv')
            df_all.to_csv(save_path)
            st.markdown(f'Dataframe saved in {save_path}')
            print(f'Dataframe saved in {save_path}')
        eva.eval()

    def read_labels(self, path):
        org_data = os.path.join(path,'data.json')
        data = super().read_data(org_data)
        org_labels = {}
        for i in data:
            org_labels[str(i['id'])] = i['label']
        return org_labels

    def set_update(self):
        super().set_update()


    '''
        def process_dataset_item(self,num_str, label_val, data_val,folder_path_val, update_val,):
        num = int(num_str)

        label = {'label':True} if label_val else {'label':False}
        info, result = super().step_tree_const(
            data_val,
            this_path=os.path.join(folder_path_val, f'{num_str}.json'),
            llm=self.llm,
            id=num_str,
            update=update_val
        )
        list_result = list(result.values())
        list_result.append(label)
        print(info)
        # reasoner = Reasoner(list_result)

        # reasoner.add_reasoner(reasoner.agg_Veto)
        # reasoner.add_reasoner(reasoner.agg_Veto)
        # reasoner.add_reasoner(reasoner.agg_Wcon_Sem)
        # sem_res = reasoner.get_result()
        # cond_sem_res = {**label, **sem_res}

        return {
            'num': num,
            'info': info,
            'result': result,
        }

    def run(self, llm):
        the_dataset = self.get_list_dataset()
        self.llm = llm
        labels = self.read_labels(the_dataset)
        datasets, folder_path = self.read_full_dataset(the_dataset)
        print(datasets)
        update = super().set_update()
        all_results = {}
        all_infos = {}
        all_cond_res = {}
        # reasoner = Reasoner()
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for num_int in range(len(datasets)):
                num_str = str(num_int)

                label_val = labels[num_str]
                data_val = datasets[num_str]

                future = executor.submit(
                    self.process_dataset_item,
                    num_str,
                    label_val,
                    data_val,
                    folder_path,  # 假设 folder_path 不变
                    update,  # 假设 update 不变

                )
                # print(future)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    num = res['num']

                    all_infos[num] = res['info']
                    all_cond_res[num] = res['result']
                    # all_results[num] = res['cond_sem_res']
                except Exception as exc:
                    print(f'Error in {exc}')


        end_time = time.time()
        st.markdown(end_time - start_time)
        # self.display_evaluation(all_results, all_cond_res, folder_path)

    def display_evaluation(self, all_results, cond_res, path):
        eva = Evaluator(all_results)

        df_cond_res = pd.DataFrame(cond_res).T
        df_results = pd.DataFrame(all_results).T
        df_cond_res = df_cond_res.add_suffix('_cond')
        df_all = pd.concat((df_cond_res, df_results), axis=1)
        st.dataframe(df_all)
        dataset_name = path.split('/')[-2]
        if st.button('SAVE RESULT'):
            save_path = os.path.join('./result/', f'{dataset_name}.csv')
            df_all.to_csv(save_path)
            st.markdown(f'Dataframe saved in {save_path}')
            print(f'Dataframe saved in {save_path}')
        eva.eval()

    '''