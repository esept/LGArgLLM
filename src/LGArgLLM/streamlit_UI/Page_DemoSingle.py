import os
import json
from copyreg import dispatch_table

import streamlit as st
import pandas as pd

from .Base_page import Base_page
from ..ARTree.ART_Viser import ART_Viser
from ..Argument_Generator import Argument_Generator
from ..ARTree import *
from ..Reasoner import Reasoner

NB_Sems = 16
DF_HEDERS = [ '1', '2', '3', '4', '5',
       '6', '7', '8', '9', '10', '11', 's',
       'p', 'm']

class Page_DemoSingle(Base_page):
    def __init__(self):
        self.path = "./data/ELSE/"
        self.this_path = None
        self.number = None
        super().__init__("DemoSingle")

    def select_claim(self):
        dataset = super().get_list_dataset()
        # st.markdown(dataset)
        dataset_name = dataset.split('/')[-1]

        all_datas, folder = super().read_full_dataset(dataset)
        claims_exists = [f'{i} - {all_datas[str(i)]["claim"]}' for i in range(len(all_datas)) ]
        num_claim = st.selectbox(
            'select claim from '+ dataset ,
            options=claims_exists
        )
        num = num_claim.split(' - ')[0]
        if st.button(f"Submit exists - {dataset_name}-{num}"):
            return num, all_datas[num], folder

    def new_claim(self):
        st.markdown("Demo claim will be save in ELSE folder")
        claim = st.text_input("Input Claim")
        if st.button("Submit New"):
            ag = Argument_Generator(self.llm)
            output = ag.get_arguments(claim)
            nb_files = len(os.listdir(self.path))
            this_path = os.path.join(self.path, f'{str(nb_files)}.json')
            # self.this_path = this_path
            super().save_json(output, this_path)
            # self.number = nb_files
            st.markdown(f'Data saved in {this_path}')
            return nb_files,output, this_path

    def run(self, llm, update=None):
        self.llm = llm
        mode = st.radio(
            "Choose mode:",
            options=["Select Existing Claim", "Create New Claim"]
        )

        if mode == "Select Existing Claim":
            result = self.select_claim()
            if result:  # 只有点击按钮后才返回值
                self.number, output, self.this_path = result
            else:
                st.stop()  # 停止执行，等待用户操作

        else:  # Create New Claim
            result = self.new_claim()
            if result:
                self.number, output, self.this_path = result
            else:
                st.stop()

        update = super().set_update()
        infos, result = super().step_tree_const(
            output,
            this_path=self.this_path,
            llm=self.llm,
            id=self.number,
            update=update
        )

        list_result = list(result.values())

        data = pd.DataFrame([list_result], columns=DF_HEDERS)
        reasoner = Reasoner()
        reasoner.get_data(data)
        self.set_reasoner(reasoner)
        sem_result = reasoner.get_results()
        '''--------<Draw Results>--------'''
        cond_res_df = pd.DataFrame([result])

        st.subheader('Condition Results')
        st.dataframe(cond_res_df)
        st.subheader('Semantic Results')
        st.dataframe(sem_result)
        '''--------<Draw ARTrees>--------'''
        self.step_vis_artrees(infos)

    def set_reasoner(self, reasoner):
        reasoner.add_reasoner(reasoner.agg_veto)
        reasoner.add_reasoner(reasoner.agg_threshold_True)
        reasoner.add_reasoner(reasoner.agg_Wc_S)
        reasoner.add_reasoner(reasoner.agg_Wc_Ws)


    def step_vis_artrees(self,infos):
        artv = ART_Viser(infos)
        artv.draw()
