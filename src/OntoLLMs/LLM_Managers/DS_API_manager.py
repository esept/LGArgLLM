from openai import OpenAI
import os

class DS_API_manager:
    def __init__(self):
        self.api_key = "sk-5a6f5c05764f4fb8af2f417254a7859d"
        self.prompt = []
        self.get_prompt()

    def get_prompt(self):
        prompt_path = "./configs/prompts"
        attack_p = os.path.join(prompt_path,'attack_yaml_prompt.txt')
        support_p = os.path.join(prompt_path,'support_yaml_prompt.txt')
        with open(support_p, 'r') as f:
            self.prompt.append(f.read()) # prompt[0]
        with open(attack_p, 'r') as f:
            self.prompt.append(f.read()) # prompt[1]
    
    def set_parameter(self, **kwargs):
        if not kwargs.get('another') and not kwargs.get('argus') and kwargs.get('claim'): # 获取支持论点 claim
            print('DS 0')
            prompt = self.prompt[0]
            text = f"Claim: {kwargs.get('claim')}"

        elif kwargs.get('prompt'): # 获取 intersection argument: prompt, argus
            print('DS 2')
            prompt = kwargs.get('prompt')
            text = f"Claim: {kwargs.get('claim')}\nAnother: {kwargs.get('argus')}"

        else: # 获取攻击森林 claim, another
            print('DS 3')
            prompt = self.prompt[1]
            text = f"Claim: {kwargs.get('claim')}\nAnother: {kwargs.get('another')}"

        return self.get_response(prompt, text)

    def get_response(self, prompt, text):
        client = OpenAI(api_key=f"{self.api_key}", base_url="https://api.deepseek.com")
        message = [
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{text}"},
        ]
        # print(message)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=message,
                stream=False
        )
        # print(message)
        res = response.choices[0].message.content
        # print(res) 
        return res
        # return response.choices[0].message.content
        
            
