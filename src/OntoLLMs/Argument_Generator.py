import os
import re
import yaml
import json
import shutil
from .LLM_Managers import LLMAPI_Manager,DS_API_manager

class Argument_Generator:
    def __init__(self, model):
        # self.model = model
        # self._llm = LLMAPI_Manager(model)
        self._llm = DS_API_manager()

    def set_claim(self, claim):
        self.claim = claim
        self._data = {'claim': claim}

    def yaml_to_json(self, yaml_content):
        try:
            data = yaml.safe_load(yaml_content)
            return data  # 直接返回Python对象
        except yaml.YAMLError as e:
            print(f"YAML Parsing Error:, {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error:, {e}")
            return None

    def fix_json_format(self, json_str):
        output_path = './data/temps/tmp_.json'

        def replace_inner_quotes(match):
            """处理 text 字段中未转义的双引号"""
            field_value = match.group(1)
            # 将非转义的双引号替换为单引号
            fixed_value = re.sub(r'(?<!\\)"', "'", field_value)
            return f'"text": "{fixed_value}"'

        try:
            # 尝试直接解析
            data = json.loads(json_str)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        except json.JSONDecodeError:
            # 第一次修复尝试
            json_str = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', json_str)

            # 处理text字段内的引号问题
            def fix_text_field(match):
                text_content = match.group(1)
                # 将文本内容中的双引号转为转义形式
                fixed_text = text_content.replace('"', '\\"')
                return '"text": "' + fixed_text + '"'

            # 找到并修复text字段
            json_str = re.sub(r'"text"\s*:\s*[\'"](.+?)[\'"](?=\s*,|\s*\})', fix_text_field, json_str)

            # 处理Sweden\'s这种情况，去掉多余的转义符
            json_str = re.sub(r'\\\'', "'", json_str)

            try:
                data = json.loads(json_str)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return data
            except json.JSONDecodeError as e:
                print(f"第二次修复失败 JSONDecodeError: {e}")
                return None

    def correct_yaml_format(self, content):
        lines = content.split('\n')
        corrected = []
        for line in lines:
            if not line.strip():  # 空行
                corrected.append(line)
                continue
            if not line.startswith('  -'):
                line = line.strip()
                line = '    ' + line
            if ': ' not in line: 
                line = line.replace(':', ': ')
            corrected.append(line)
        return '\n'.join(corrected)  

    def generate_support_argus(self):
        save_path = "./data/temps"
        output = self._llm.set_parameter(claim=self.claim) # LLM MANAGER
        
        print(output)
        output_rp = output.replace('```yaml','').replace('```','').replace('。','.')
        output_rp = output_rp.replace('：',':')
        support_args = self.yaml_to_json(output_rp)

        return support_args['Arguments'],support_args['Confidence']

    def generate_attack_argus(self, this_argu):
        output = self._llm.set_parameter(
            # prompt=self._llm.prompt[1],
            claim=self.claim,
            another=this_argu
        )
        # print(output)

        output_rp = output.replace('```yaml','').replace('```','').replace('。','.')
        output_rp = output_rp.replace('：',':').replace(":[",": [").replace(":0",": 0")
        attack_argu = self.yaml_to_json(output_rp)

        return attack_argu['Arguments']

    def remove_temp_files(self):
        save_path = "./data/temps/"
        for file in os.listdir(save_path):
            file_path = os.path.join(save_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


    def generate_AttackData(self):
        self.remove_temp_files()
        sas, conf = self.generate_support_argus()
        print(conf)
        # print(sas)
        # with open("./data/temps/2-step.json", 'w') as f:
        #     json.dump(sas, f, indent=2, ensure_ascii=False)
        self._data['score'] = conf
        self._data['Args'] = {}
        # print(sas)
        for idx, sa in enumerate(sas):
            # print('--'+ sa['id'] +'--')
            
            attack_ag = self.generate_attack_argus(sa)
            self._data['Args'][f'A{idx+1}'] = {
                'supporting': sa,
                'attacks': attack_ag
            }
            print(attack_ag)
        return self._data