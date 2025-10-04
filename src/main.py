import argparse
from LGArgLLM.LGArgLLM_pipeline import LGArgLLM_pipeline



if __name__ == "__main__":
    print("<--------------- LGArgLLM --------------->")

    parser = argparse.ArgumentParser(description="LGArgLLM")
    parser.add_argument(
        "-m", "--mode", type=str, default="ui", help="ui-WebPageUI, nd-NewDataset"
    ) # 模式 

    parser.add_argument(
        "-dp", "--dataset", type=str, help="Dataset Path"
    )

    parser.add_argument(
        "-llm", "--model", type=str, default="deepseek"
    )


    args = parser.parse_args()
    the_mode = args.mode
    the_data = args.dataset
    the_llm = args.model
    print(the_data, the_mode)
    pipeline = LGArgLLM_pipeline(the_mode, the_data, the_llm)









    



