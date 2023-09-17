from agent_mediator.llm_mediator import llm_mediator
import json
ruta_config = "config/config.json"

class Agent(object):

    def __init__(self, agent_id, name, role, bio) ->  None:

        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.bio = bio
        self.agent_system_context = ""
        self.llm_answer_format = ""
        self.llm_mediator = llm_mediator()

        self.initializate_agent_system_context()
        #print(self.agent_system_context)
    
    def __str__(self) -> str:
        return "%s: { name: %s, rol: %s, bio: %s}" % (self.agent_id, self.name, self.role, self.bio)
    
    def initializate_agent_system_context(self):
        # Lee el archivo config.json
        with open(ruta_config, "r") as archivo:
            config = json.load(archivo)
            
        variables = {
        "agent_id": self.agent_id,
        "agent_name": self.name,
        "agent_role": self.role,
        "agent_bio": self.bio,
        }

        with open(config["SYSTEM_CONTEXT_PATH"] +"/global_context.txt", 'r') as file:
            self.agent_system_context = file.read() 

        with open(config["GENERIC_DATA"]+"/agent_context_format.txt", 'r') as file:
            generic_agent_bio = file.read()
        
        agent_bio_formated = generic_agent_bio.format(**variables)

        with open(config["GENERIC_DATA"]+"/llm_answer_format.txt", 'r') as file:
            self.llm_answer_format = file.read()
        
        self.agent_system_context = self.agent_system_context + "\n" + agent_bio_formated 

        self.llm_mediator.define_initial_and_format_context(self.agent_system_context, self.llm_answer_format)

    async def create_llm_individual_query(self, individual_query):
        #print("\n--------------------------- individual_query ---------------------------\n ", individual_query)
        llm_response = await self.llm_mediator.get_response(individual_query)
        return llm_response

        