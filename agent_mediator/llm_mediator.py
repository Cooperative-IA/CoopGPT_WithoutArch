import os

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = "https://invuniandesai.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = "cf0bd49030ed4aa6a6509be1cd9d604b"

import openai
import json
import ast


#TODO cambiar la parametrización desde un archivo de configuración

class llm_mediator(object):
    def __init__(self):
        self.engine_name =  "gpt-35-turbo-16k-rfmanrique"
        self.data_path = "/home/jeyseb/MeltingPot/CoopGPT_WithoutArch/data/"
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
            engine="gpt-35-turbo-16k-rfmanrique",
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