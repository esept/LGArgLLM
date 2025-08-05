import os
import requests


class LLMAPI_Manager:
    def __init__(self, model='Pro/deepseek-ai/DeepSeek-V3'):
        self._model = model
        self.prompt = []
        self.get_prompt()
        self._KEY = 'sk-bwoagxuqyasxezxxnpbskbculhwrmlnvigsbxffyvwdfnjbz'
        self.url = "https://api.siliconflow.cn/v1/chat/completions"

    def get_prompt(self):
        prompt_path = "./configs/prompts"
        attack_p = os.path.join(prompt_path,'attack_yaml_prompt.txt')
        support_p = os.path.join(prompt_path,'support_yaml_prompt.txt')
        with open(support_p, 'r') as f:
            self.prompt.append(f.read()) # prompt[0]
        with open(attack_p, 'r') as f:
            self.prompt.append(f.read()) # prompt[1]

    def get_argument(self, claim, another=None):
        if another is None:
            prompt = self.prompt[0]
            text = f'claim: {claim}'
        else:
            prompt = self.prompt[1]
            text = f'claim: {claim} \nSupport Argument: {another}'
        # print(prompt)
        payload = {
            "model": f'{self._model}',
            "messages": [
                {
                    "role": "system",
                    "content": f"{prompt}" # LLM 系统设定
                },
                {
                    "role": "user",
                    "content": f"\n{text}" # 处理内容
                }
            ],
            "stream": False,
            "temperature": 0.5,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1
        }

        headers = {
            "Authorization": f"Bearer {self._KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            return response_data

        return response_data['choices'][0]['message']['content']


    def get_reasoning(self, prompt, another):
        payload = {
            "model": f'{self._model}',
            "messages": [
                {
                    "role": "system",
                    "content": f"{prompt}" # LLM 系统设定
                },
                {
                    "role": "user",
                    "content": f"\n{another}" # 处理内容
                }
            ],
            "stream": False,
            "temperature": 0.5,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1
        }

        headers = {
            "Authorization": f"Bearer {self._KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            return response_data

        return response_data['choices'][0]['message']['content']
