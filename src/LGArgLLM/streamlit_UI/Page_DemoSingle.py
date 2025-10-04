import os
import json
import streamlit as st
import pandas as pd

from .Base_page import Base_page
from ..ARTree.ART_Viser import ART_Viser
from ..Argument_Generator import Argument_Generator
from ..ARTree import *
from ..Reasoner import Reasoner

NB_Sems = 16

class Page_DemoSingle(Base_page):
    def __init__(self):
        self.path = "./data/ELSE/"
        self.this_path = None
        self.number = None
        super().__init__("DemoSingle")

    def run(self, llm):
        self.llm = llm
        st.markdown("Demo claim will be save in ELSE folder")
        # self.llm = super().choose_llm()
        claim = st.text_input("Input Claim")
        output = None

        if st.button("Submit"):
            # '''
            ag = Argument_Generator(self.llm)
            output = ag.get_arguments(claim)
            nb_files = len(os.listdir(self.path))
            this_path = os.path.join(self.path, f'{str(nb_files)}.json')
            self.this_path = this_path
            super().save_json(output, this_path)
            self.number = nb_files
            st.markdown(f'Data saved in {this_path}')
            '''
            output = super().read_data("./data/ELSE/89.json")
            self.this_path = "./data/ELSE/89.json"
            self.number = 89
            '''
            update = super().set_update()
            infos, result = super().step_tree_const(
                output,
                this_path=self.this_path,
                llm=self.llm,
                id=self.number,
                update=update
            )

            list_result = list(result.values())
            reasoner = Reasoner(list_result)

            reasoner.add_reasoner(reasoner.agg_veto)
            reasoner.add_reasoner(reasoner.agg_threshold_True)

            sem_result = reasoner.get_result()
            '''--------<Draw Results>--------'''
            cond_res_df = pd.DataFrame([result])
            sem_res_df = pd.DataFrame([sem_result])

            st.subheader('Condition Results')
            st.dataframe(cond_res_df)
            st.subheader('Semantic Results')
            st.dataframe(sem_res_df)
            '''--------<Draw ARTrees>--------'''
            self.step_vis_artrees(infos)


    def step_vis_artrees(self,infos):
        artv = ART_Viser(infos)
        artv.draw()
