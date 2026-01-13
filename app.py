import os
import json
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from pinecone import Pinecone
pine_api = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pine_api)
index = pc.Index(host="https://avenchatbot-rz0q9xs.svc.aped-4627-b74a.pinecone.io")

def vector_search(prompt):
    search = index.search(
            namespace = "default",
            query = {
                "inputs": {"text": prompt},
                "top_k": 4
            },
            fields = ["category", "chunk_text"],
            rerank = {
                "model": "bge-reranker-v2-m3",
                "top_n": 4,
                "rank_fields": ["chunk_text"] 
            }
        )
    print("SEARCH RESULT ", search)
    n = len(search['result']['hits'])
    vknowledge = [
        search['result']['hits'][i]['fields']['chunk_text'] for i in range(n) if search['result']['hits'][i]['_score'] > 0.35
    ]
    return vknowledge

import replicate
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

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
    
Assistant = TextModel(
    "meta/meta-llama-3-8b-instruct",
    """
    Context: You are Aven's intelligent chat assistant, designed to assist users with their queries—especially those related to financial services, products, or policies offered by Aven (note: Aven might be misspelled as Even, Avian, Evan, etc.).
    
    Instructions:
    - Do not assume information regarding Aven. Only use provided knowledge for answering.
    - Always reply in JSON format.
    - Use any of the provided tools to gather knowledge from sources if need be.
    - Do not engage in conversation if it strayss off topic since it increases cost.
    - Be polite & concise.

    Output templates:
    1. If query can be answered without need of additional knowledge.
    Respond with - 
    {
        "type": "answer",
        "content": "<Your concise and polite response here>"
    }
    2. If additional information is needed for answering query.
    Respond with - 
    {
        "type": "vector",
        "content": "<Your prompt to search vector/web with>"
    }
    VectorDB has vast information regarding Aven. 
    The prompt will contain your action history i.e. previous Vector searches.
    Do not use "/" in your replies.
    Answer appropriately when you can not find appropriate knowledge to answer the query.

    Vector search can only be used once. If any information is present under ### Current Knowledge, do not use Vector Search at any cost.
    """
)

class ProcessState(TypedDict):
    conversation: str
    knowledge: str
    response: str
    reply: str

def choose(state: ProcessState):
    print("Choose ", state)
    conversation = state["conversation"]
    knowledge = state["knowledge"]
    response = state["response"]
    reply = state["reply"]

    prompt = f"""
    ### Conversation
    {conversation}

    ### Current Knowledge
    {knowledge}

    ### Available Actions
    vector
    """
    response = Assistant.gen(prompt)
    return {
        "response": response,
        "knowledge": knowledge,
        "reply": reply,
        "conversation": conversation
    }

def route(state: ProcessState) -> str:
    response = state["response"]
    print(response)
    response = json.loads(response)
    return response["type"]

def go_vector(state: ProcessState):
    conversation = state["conversation"]
    knowledge = state["knowledge"]
    response = state["response"]
    reply = state["reply"]
    print("GOVECTOR", state)
    response = json.loads(state["response"])
    info = vector_search(response["content"])
    knowledge = state["knowledge"]
    knowledge += f"""
    -> VECTOR SEARCH "{response["content"]}" KNOWLEDGE
    {info}
    """
    return {
        "response": response,
        "reply": reply,
        "conversation": conversation,
        "knowledge": knowledge
    }

def give_reply(state: ProcessState):
    conversation = state["conversation"]
    knowledge = state["knowledge"]
    response = state["response"]
    reply = state["reply"]
    print("SENDREPLY", state)
    response = json.loads(state["response"])
    reply = response["content"]
    return {
        "response": response,
        "conversation": conversation,
        "knowledge": knowledge,
        "reply": reply
    }

chat_graph = StateGraph(ProcessState)
chat_graph.add_node("choose", choose)
chat_graph.add_node("go_vector", go_vector)
chat_graph.add_node("give_reply", give_reply)

chat_graph.add_edge(START, "choose")
chat_graph.add_conditional_edges(
    "choose",
    route,
    {
        "answer": "give_reply",
        "vector": "go_vector"
    }
)
chat_graph.add_edge("go_vector", "choose")
chat_graph.add_edge("give_reply", END)

compiled_graph = chat_graph.compile()



from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/respond', methods=['GET', 'POST'])
def respond():
    data = request.get_json()
    user_message = data.get('messages', '')
    history = ""
    for i in user_message[:-1]:
        if i['role'] == 'user':
            history += "User: " + i['text'] + "\n"
        elif i['role'] == 'bot':
            history += "You: " + i['text'] + "\n"
    history += "You: "
    final_state = compiled_graph.invoke({
        "conversation": history,
        "knowledge": "",
        "response": "",
        "reply": ""
    })
    reply = final_state['reply'].replace("\\n","<br>")
    return jsonify({"message": reply})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  
    app.run(host='0.0.0.0', port=port, debug=True)

