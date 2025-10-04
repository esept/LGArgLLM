import streamlit as st
import pandas as pd


class Evaluator:
    def __init__(self, data):
        self.data = data


    def eval(self):
        nb_sems_true = {key: 0 for key in list(self.data.keys())[1:]}
        self.length = 0
        data = (pd.DataFrame(self.data).T).to_dict()
        for key in data:
            self.length += 1
            this_line = data[key]
            label = this_line['label'] == True
            for key in nb_sems_true:
                nb_sems_true[key] += int(label == this_line[key])
        percentage = {i: nb_sems_true[i]/self.length for i in nb_sems_true}

        the_sum = sum([nb_sems_true[i] for i in nb_sems_true])
        st.markdown(f"**Total Correct Number: {the_sum}**")
        df_res = pd.DataFrame({
            'Count': nb_sems_true,
            'Percentage': percentage
        }).T

        st.dataframe(df_res)






