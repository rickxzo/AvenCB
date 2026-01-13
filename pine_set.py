import requests
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host="https://avenchatbot-rz0q9xs.svc.aped-4627-b74a.pinecone.io")

import replicate
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

url = "https://aven.com/support"
response = requests.get(url)
response.raise_for_status()

class TextModel:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
    
    def gen(self, prompt):
        input = {
            "prompt": prompt,
            "system_prompt": self.system_prompt,
        }
        x = ''
        for event in replicate.stream(
            self.model_name,
            input=input
        ):
            x += str(event)
        return x
    
Agent = TextModel(
    "openai/gpt-5",
    """
    Summarize the input text in upto 15 words (STRICT).
    Guranteed shut down upon surpassing 15+ words. Avoid.

    Answer with 'none' when the input seems random text instead of a potential
    answer to an question.
    """
)


soup = BeautifulSoup(response.text, "html.parser")
li_elements = soup.find_all("li")

results = []

for i in li_elements:
    if len(str(i.get_text(strip=True)))<30:
        ques = 'none'
        ans = 'none'
    else:
        info = str(i.get_text(strip=True))
        info = info.split("?")
        if len(info)<2:
            ques = Agent.gen(str(info))

            ans = info
        else:
            ques = info[0]
            ans = info[1]
        if ques!='none':
            results.append([str(ques), str(ans)])
            print("ques\n", ques, "\n")
            print("ans\n", ans, "\n\n\n")



def to_ascii_id(text):
    return text.encode("ascii", "ignore").decode().strip()

n = len(results)
print(n)
for i in results:
    index.upsert_records(
        "default",
        [
            {
                "_id": to_ascii_id(i[0]),
                "chunk_text": i[1],
                "category": "FAQ"
            }
        ]
    )


