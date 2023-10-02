import os
from dotenv import load_dotenv
load_dotenv()

env = os.getenv("ENV")
os.environ["OPENAI_API_TYPE"] = os.getenv("OPENAI_API_TYPE")    
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT_GPT3")
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY_GPT3")

import openai
import json
import ast


#TODO cambiar la parametrización desde un archivo de configuración

class llm_mediator(object):
    def __init__(self):
        self.engine_name =  os.getenv("GPT_35_MODEL_ID")
        self.data_path = os.getenv("DATA_PATH")
        self.initial_context = ""
        self.format_example = ""
        self.messages_history = {}

    def define_initial_and_format_context(self, agent_initial_context, agent_format_example):

        messages_history = [
                {"role": "system", "content": agent_initial_context},
                {"role": "user", "content": agent_format_example},
                {"role": "assistant", "content": "Right"}
                ]
        self.messages_history = messages_history
    
    async def get_response(self, query):
        # append the new query to the messages history
        current_messages_history = self.messages_history.copy()
        
        current_messages_history.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            engine=self.engine_name,
            messages=self.messages_history,
            )   
        # append the new response to the messages history
        #self.messages_history.append({"role": "assistant", "content": response.choices[0].message.content})

        llm_actions = response.choices[0].message.content
        llm_actions.replace('\n', ' ')

        #Transformar de json a diccionario
        llm_actions_dict = ast.literal_eval(llm_actions)
        
        return llm_actions_dict
    



    def get_default_response(self):
        llm_actions = "{ 'Agent0': { 'Future Goals': ['explore'], 'Action': ['move 1 step downward']  },\
                    'Agent1': {'Future Goals': ['go for apples', 'gather apples'], 'Action': ['move 1 step upward'] },\
                    'Agent2': { 'Future Goals': ['go for apples', 'gather apples'], 'Action': ['move 1 step on the left'] } }"
        llm_actions.replace('\n', ' ')
        
        llm_actions_dict = ast.literal_eval(llm_actions)

        return llm_actions_dict