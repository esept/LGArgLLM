from OntoLLMs import *
from OntoLLMs.utils import *
from OntoLLMs.Ensemble import Ensemble
import os
import json

# org_path = './data/Truth_data/data_truthful_prompt.json'
# file_path = './data/Truth_data/dpsk_Tests1'

# if __name__ == "__main__":
#     with open(org_path,'r') as f:
#         content = f.read()
#     org_data = json.loads(content)
    
#     files = []
#     for file in os.listdir(file_path):
#         if file.endswith('json'):
#             files.append(os.path.join(file_path, file))
#     # print(files)
#     for file in files:
#         with open(file, 'r') as f:
#             content = f.read()
#         this_data = json.loads(content)
#         this_claim = this_data['claim']
#         for item in org_data:
#             if this_claim == item['claim']:
#                 print(file, item['id'])
                # break

    
# if __name__ == "__main__":
#     path = "../wrong"
#     cc = [i.split('.')[0] for i in os.listdir(path) if i.endswith('json')]
#     print(cc)
#     dpath = "./data/Truth_data/data_truthful_prompt.json"
#     with open(dpath,'r') as f:
#         content = f.read()
#     org_data = json.loads(content)
#     wrong_data = []
#     for item in org_data:
#         if str(item['id']) in cc:
#             wrong_data.append(item)
#     "./data/Wrong_data"
#     with open('./data/Wrong_data/data_wrong.json','w') as f:
#         json.dump(wrong_data, f, ensure_ascii=False, indent=4)
#     # for data in cc:
        


if __name__ == "__main__":
    # read_Truthfulqa()
    # first_path = "./data/Truthful_Prompt.csv"
    first_path = "./results/truthfulqa.csv"
    # second_path = "./data/evaluation_results.csv"
    e = Ensemble(first_path)
    e.single_source()
    # e.double_source()