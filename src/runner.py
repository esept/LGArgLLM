from OntoLLMs.OntoLLMsPipeline import OntoLLMsPipeline

MODES = [
    "EVA", # evaluation 
    "ND", # new data
    "DEMO" # demo 
]

DATA_PATH = [
    "./data/Truth_data/data_truthful_prompt.json",
    "./data/MedQA_data/data_medqa.json",
    "./data/ME_data/data_me.json",
    "./data/Wrong_data/data_wrong.json",
    "./data/Mel_data/data_mel.json",
    "./data/Strategy_data/data_Strategy_prompt.json",
    "./data/d2_data/data_d2.json",
    "./data/d3_data/data_d3.json",
    "./data/tt_data/data_tt.json",
]

if __name__ == "__main__":
    Mode = MODES[2]
    pl = OntoLLMsPipeline()
    pl.runner(Mode, data_path=DATA_PATH[1])


    
