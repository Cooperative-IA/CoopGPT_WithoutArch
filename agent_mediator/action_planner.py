import asyncio
import subprocess
import re
import json
import ast
from agent_mediator.llm_mediator import llm_mediator
from agent_mediator.agent import Agent

ruta_config = "config/config.json"  

_BASE_ACTION_MAP = {
    0:{
    'move': 0,
    'turn': 0,
    'fireZap': 0
    },
    1:{
    'move': 0,
    'turn': 0,
    'fireZap': 0 
    },    
    2:{
    'move': 0,
    'turn': 0,
    'fireZap': 0 
    }
}
_ACTION_MAP = {
    0:{
    'move': 0,
    'turn': 0,
    'fireZap': 0
    },
    1:{
    'move': 0,
    'turn': 0,
    'fireZap': 0 
    },    
    2:{
    'move': 0,
    'turn': 0,
    'fireZap': 0 
    }
}


class ActionPlanner(object):
    
    def __init__(self, agents_count, agents_bio_path):
        self.agents_current_goals ={}
        self.agents_count = agents_count
        self.agents_bio_path = agents_bio_path

        # Initialize the global system context
        self.initialize_system_context(agents_count, number_of_roles = 1)
        # Create the agents list
        self.agents_dictionary = self.initialize_agents_bio()

    def initialize_agents_bio(self):
        agents_dictionary = {}
        agents_bio = {}
        with open(self.agents_bio_path, 'r') as file:
            agents_bio = json.load(file)
        
        for _, agent_bio in agents_bio.items():
            agent_object = Agent(agent_bio["Agent_id"], agent_bio['Name'], agent_bio['Role'], agent_bio['Bio'])    
            agents_dictionary[agent_object.agent_id] = agent_object

        #print([str(agent) for agent in agents_list])
        return agents_dictionary

    def initialize_system_context(self,number_of_agents, number_of_roles):
        ## TODO cargar el role description desde un archivo
        role_descriptions = "- Consumer role: The primary goal of a Consumer agent is to maximize their reward by efficiently collecting apples and avoiding unnecessary actions.\n\
                                Valid actions for Consumer Role: {move {right, left, upward, downward}, attack <player>}.\n"
        
        each_agent_description = ""
        with open(self.agents_bio_path, 'r') as file:
            agents_bio = json.load(file)
        
        for _, agent_bio in agents_bio.items():
            each_agent_description += " - %s: {{Name: %s; Role: %s; Description: %s}}\n" % (agent_bio["Agent_id"], agent_bio['Name'], agent_bio['Role'], agent_bio['Bio'][:agent_bio['Bio'].find('person')+6])

        variables = {
            "number_of_roles": number_of_roles,
            "kind_of_roles": "Consumer",
            "each_role_description": role_descriptions,
            "number_of_agents": number_of_agents,
            "each_agent_description": each_agent_description,
        }

        with open(ruta_config, "r") as archivo:
            config = json.load(archivo)

        ## cargar el boceto del texto del contexto inicial desde generic_context.txt
        with open(config["GENERIC_DATA"]+"/global_context.txt", 'r') as file:
            system_context = file.read()#.replace('\n', ' ')
        ## reemplazar las variables en el texto del contexto inicial
        system_context_formated = system_context.format(**variables)

        ## guardar el texto del contexto inicial en un archivo
        with open(config["SYSTEM_CONTEXT_PATH"]+'/global_context.txt', 'w') as file:
            file.write(system_context_formated)
        


    def get_current_direction(self, agent_id):
        return _ACTION_MAP[agent_id]['move']

    def get_current_turn(self, agent_id):
        return _ACTION_MAP[agent_id]['turn']

    def get_current_fire(self, agent_id):
        return _ACTION_MAP[agent_id]['fireZap']


    def retrieve_agent_observations(self, agents_observations_str: str):
        agents_observations = ast.literal_eval(agents_observations_str)
        for agent in agents_observations:
            agent_dict = agents_observations[agent]
            agent_dict['objects']={}
            if agent_dict['observation'].startswith('You were taken'):
                agent_dict['objects']['takenby'] = agent_dict['observation'].split(' ')[-1]
                continue

            bool_agent_seen = False
            id_arbol_actual = 0
            observation_matrix = agent_dict['observation'].split('\n')
            i=0
            for row in observation_matrix:
                j=0
                for char in row:

                    if char == '#':
                        agent_dict['objects']['self position'] = i, j 
                    elif re.match(r'^[0-9]$', char):
                        dict_of_agents = agent_dict['objects'].get('agents_observed_pos',{})
                        dict_of_agents[char] = (i, j)
                        agent_dict['objects']['agents_observed_pos'] = dict_of_agents
                    elif char == 'W':
                        if 'WW' in row and not bool_agent_seen:
                            agent_dict['objects']['upper wall'] = i, 0 
                        elif 'WW' in row  and bool_agent_seen:
                            agent_dict['objects']['bottom wall'] = i, 0 
                        elif j == 0:
                            agent_dict['objects']['left wall'] = 0, j 
                        else: 
                            agent_dict['objects']['right wall'] = 0, j 
                    elif (char == 'A' or char == 'G') and not self.tree_already_exists(agent_dict, i, j):

                        new_tree = self.create_tree( observation_matrix, i, j)
                        agent_dict['objects']['apple tree'] = agent_dict['objects'].get("apple tree", {} ) 
                        agent_dict['objects']['apple tree'][id_arbol_actual] = new_tree

                        id_arbol_actual+=1
                    j+=1
                i+=1
                
        return agents_observations

    def create_tree(self, observation_matrix, i, j):
        growing_apples = []
        apples = []
        x, y = j, i

        for y_sign in [-1, 1]:
            y = i
            x = j
            #print(observation_matrix, y, x, observation_matrix[y][x] )  
            while observation_matrix[y][x] in ['A','G']:

                for x_sign in [-1, 1]:
                    x = j
                    while observation_matrix[y][x] in ['A','G']:
                        if observation_matrix[y][x] == 'A' and (y,x) not in apples:
                            apples.append((y,x))
                        elif observation_matrix[y][x] == 'G' and (y,x) not in growing_apples:
                            growing_apples.append((y,x))
                        x+=x_sign

                        if x >= len(observation_matrix[0]) or x < 0:
                            break
                y+=y_sign
                x = j
                if y >= len(observation_matrix) or y < 0:
                    break

        center = apples[len(apples)//2] if len(apples) > 0 else growing_apples[len(growing_apples)//2]
        return {'growing':growing_apples, 'apples':apples, 'center': center}
    

    def create_tree_v0(self, observation_matrix, i, j):
        growing_apples = []
        apples = []

        for k in range(-2,3):
            for l in range (-2,3):
                x = j+k
                y = i+l
                if x < 0 or x >= len(observation_matrix) or y < 0 or y >= len(observation_matrix[0]):
                    continue
                if observation_matrix[x][y] == 'A':
                    apples.append((x,y))
                elif observation_matrix[x][y] == 'G':
                    growing_apples.append((x,y))

        return {'growing':growing_apples, 'apples':apples, 'center':(i,j+2)}

    def tree_already_exists(self, agent_dict, i, j):
        for tree in agent_dict['objects'].get('apple tree',{}).values():
            if (i, j) in tree['growing'] or (i, j) in tree['apples']:
                return True
        return False
        
    def get_closest_apple(self, ag_x, ag_y, agent_dict):
        closest_apple = None
        closest_distance = 1000
        closest_tree_id = None
        for tree_id, tree in agent_dict['apple tree'].items():
            for apple in tree['apples']:
                distance = abs(ag_x - apple[0]) + abs(ag_y - apple[1])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_apple = apple
                    closest_tree_id = tree_id
        return closest_apple, closest_tree_id


    def agent_observations_descriptor(self, agents_observations:dict):
        agents_obs_descriptor = {}
        for agent in agents_observations:
            agent_objets_dict = agents_observations[agent]['objects']
            agent_objets_dict['agents observed'] =  agents_observations[agent]['agents_in_observation']
            self_pos = agent_objets_dict.get('self position', 'dead')

            #agent_observation = 'Observations: [' %agent 
            agent_observation = '[ '
            for kind, value in agent_objets_dict.items():
                #agent_observation+='{ observed {kind} at {value} }'
                if kind == 'self position':
                    continue
                elif kind == 'takenby':
                    agent_observation+='{This agent was taken by %s }' % value
                    break
                    
                elif kind in ['upper wall', 'bottom wall']:
                    v_dir_center = 'upward' if kind.split(' ') else 'downward'
                    agent_observation+='{ observed a %s %s steps %s }, ' % ('wall', str(abs(value[0]-self_pos[0])), 'upward')
                elif kind == 'bottom wall':
                    agent_observation+='{ observed a %s %s steps %s }, ' % ('wall', str(abs(value[0]-self_pos[0])), 'downward')
                elif kind == 'left wall':
                    agent_observation+='{ observed a %s %s steps %s }, ' % ('wall', str(abs(value[1]-self_pos[1])), 'on the left')
                elif kind == 'right wall':
                    agent_observation+='{ observed a %s %s steps %s }, ' % ('wall', str(abs(value[1]-self_pos[1])), 'on the right')
                elif kind == 'apple tree':

                    #print("\n------------------------------ APPLE TREES ------------------------------\n", value)
                    for tree_id, tree in value.items() :

                        tree_centroid = tree['center']
                        h_dir_center = 'on the left' if tree_centroid[1] < self_pos[1] else 'on the right' if tree_centroid[1] > self_pos[1] else 'horizontal'
                        v_dir_center = 'up' if tree_centroid[0] < self_pos[0] else 'down' if tree_centroid[0] > self_pos[0] else 'vertical'
                        h_steps_center = abs(tree_centroid[1]-self_pos[1])
                        v_steps_center = abs(tree_centroid[0]-self_pos[0])


                        agent_observation+='{ observed the apple tree tree_%s, centroid is at %s steps %s and %s steps %s ( %s total steps needed to reach it)'\
                                                 % ( str(tree_id), str(v_steps_center), v_dir_center, str(h_steps_center), h_dir_center , str(v_steps_center+h_steps_center))
                    
                    closest_apple, tree_id_param = self.get_closest_apple(self_pos[0], self_pos[1], agent_objets_dict)
                    if closest_apple is not None:
                        h_dir = 'left' if closest_apple[1] < self_pos[1] else 'right' if closest_apple[1] > self_pos[1] else 'horizontal'
                        v_dir = 'up' if closest_apple[0] < self_pos[0] else 'down' if closest_apple[0] > self_pos[0] else 'vertical'
                        h_steps = abs(closest_apple[1]-self_pos[1])
                        v_steps = abs(closest_apple[0]-self_pos[0])



                        agent_observation+='. The closest apple (from tree %s) is at %s steps %s and %s steps %s ( %s total steps needed to reach it)'\
                                                                    % ( tree_id_param, str(v_steps), v_dir, str(h_steps), h_dir , str(v_steps+h_steps))
                    agent_observation+=' }, '
                elif kind == 'agents observed' and len(value) > 0:
                    if len(value) == 0:
                        continue
                    agent_observation+='{agents observed: '
                    for agent_id, agent_name in value.items():
                        agent_pos = agent_objets_dict['agents_observed_pos'][agent_id]
                        v_dir_center = 'upward' if agent_pos[0] < self_pos[0] else 'downward'
                        h_dir_center = 'on the left' if agent_pos[1] < self_pos[1] else 'on the right'
                        agent_observation+=' Agent %s (%s) %s steps %s and %s steps %s ; ' % (agent_id, agent_name, str(abs(agent_pos[0]-self_pos[0])), v_dir_center, str(abs(agent_pos[1]-self_pos[1])), h_dir_center)
                    
                    agent_observation+='} '
            agent_observation+=']'
            agents_obs_descriptor[agent] = agent_observation
        return agents_obs_descriptor

    #TODO revisar lo de current goals   
    def create_querys(self,agents_obs_descriptor:dict):

        query_dict = {}

        for agent_index in agents_obs_descriptor:
            agent_id = "agent_%s" % str(int(agent_index)+1)
            query_dict[agent_id] = {"Current Goals":self.agents_current_goals.get(agent_id, [])
                                    , "Observations":agents_obs_descriptor[agent_index]}

        # convertir query dict a string
        query_dict

        return query_dict


    def llm_actions_translator(self, llm_actions:dict):
        i=0
        for agent in llm_actions:

            self.agents_current_goals[agent] = llm_actions[agent]['Future Goals']

            tokens =llm_actions[agent]['Action'][0].split(' ')
            if tokens[0] == 'move':
                int_direction = 1 if tokens[-1].startswith('up') else 3 if tokens[-1].startswith('down')\
                                    else 4 if tokens[-1] == 'left' else 2  if  tokens[-1] == 'right'\
                                    else 0
                _ACTION_MAP[i]['move'] = int_direction
            elif tokens[0] == 'turn':
                int_direction = -1 if tokens[-1] == 'left' else 1 if tokens[-1] == 'right' else 0
                _ACTION_MAP[i]['turn'] = int_direction
            elif tokens[0] == 'attack':
                _ACTION_MAP[i]['fireZap'] = 1 
            i+=1
        return _ACTION_MAP




    matrix_conversor_path = "test_substrate.py"

    async def transform_obs_into_actions(self, description:str):
        #input("Press Enter to continue...")
        print(description.strip())
        agent_obs = self.retrieve_agent_observations(description.strip())
        agent_obs_desc = self.agent_observations_descriptor(agent_obs)


        querys_dict = self.create_querys(agent_obs_desc) 
        print("--------------QUERYS DICT------------------------\n",querys_dict,"\n--------------------------------------\n")
        
            
        llm_querys = [self.agents_dictionary[agent_id].create_llm_individual_query(str(query)) for agent_id, query in querys_dict.items()]
        llm_actions_list = await asyncio.gather(*llm_querys)
        llm_actions = {}
        for llm_act in llm_actions_list:
            llm_actions.update(llm_act)
        print("-----------------LLM ACTIONS--------------------\n", llm_actions,"--------------------------------------\n")
        
        #llm_actions = llm_med.get_default_response()
        #print(llm_actions)
        agents_action_map = self.llm_actions_translator(llm_actions) 

                
        return agents_action_map