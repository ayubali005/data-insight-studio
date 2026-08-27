import json, os, re
from typing import Dict
import requests

SYSTEM = """You generate concise pandas analysis code. Return JSON with keys explanation, code, chart.
Rules: use only the provided dataframe names; use pandas and matplotlib; never read/write files, import os/subprocess/sys/socket, or access the network. Put the final useful object in a variable named result. If a chart helps, create it with matplotlib. Do not call plt.show()."""

class LLMClient:
    def __init__(self):
        self.provider=os.getenv('AI_PROVIDER','groq').lower()
        self.groq_key=os.getenv('GROQ_API_KEY','')
        self.openai_key=os.getenv('OPENAI_API_KEY','')
        self.model=os.getenv('GROQ_MODEL','llama-3.3-70b-versatile') if self.provider=='groq' else os.getenv('OPENAI_MODEL','gpt-4o-mini')

    def available(self):
        return bool(self.groq_key if self.provider=='groq' else self.openai_key)

    def generate(self, question: str, schemas: Dict[str,str]):
        prompt = SYSTEM + "\n\nDATASETS:\n" + json.dumps(schemas, indent=2) + f"\n\nQUESTION:\n{question}"
        if not self.available():
            return None
        if self.provider=='groq':
            url='https://api.groq.com/openai/v1/chat/completions'; key=self.groq_key
        else:
            url='https://api.openai.com/v1/chat/completions'; key=self.openai_key
        r=requests.post(url, headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},
                        json={'model':self.model,'temperature':0.1,'response_format':{'type':'json_object'},
                              'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]}, timeout=90)
        r.raise_for_status()
        text=r.json()['choices'][0]['message']['content']
        return json.loads(text)


def extract_code(text: str)->str:
    m=re.search(r'```(?:python)?\s*(.*?)```', text, re.S|re.I)
    return m.group(1).strip() if m else text.strip()
