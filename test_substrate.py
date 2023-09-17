import json
import ast
import sys
import argparse
from absl import app
from absl import flags
from ml_collections import config_dict
from substrates.installer import install_substrate
from substrates.python import commons_harvest_language as game
from playing_utils import level_playing_utils as level_playing_utils
import asyncio

FLAGS = flags.FLAGS

flags.DEFINE_integer('screen_width', 800,
                     'Width, in pixels, of the game screen')
flags.DEFINE_integer('screen_height', 600,
                     'Height, in pixels, of the game screen')
flags.DEFINE_integer('frames_per_second', 8, 'Frames per second of the game')
flags.DEFINE_string('observation', 'RGB', 'Name of the observation to render')
flags.DEFINE_bool('verbose', False, 'Whether we want verbose output')
flags.DEFINE_bool('display_text', False,
                  'Whether we to display a debug text message')
flags.DEFINE_string('text_message', 'This page intentionally left blank',
                    'Text to display if `display_text` is `True`')


def read_action_map ():
    for line in sys.stdin:
        print("Received message:", line.strip())
        return ast.literal_eval(line.strip())
    

def get_current_direction(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['move']

def get_current_turn(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['turn']

def get_current_fire(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['fireZap']


_ACTION_MAP = {
    0:{
    'move': level_playing_utils.get_direction_pressed,
    'turn': level_playing_utils.get_turn_pressed,
    'fireZap': level_playing_utils.get_space_key_pressed
    },
    1:{
    'move': level_playing_utils.get_random_direction,
    'turn': level_playing_utils.get_random_turn,
    'fireZap': level_playing_utils.get_random_fire 
    },    
    2:{
    'move': level_playing_utils.get_random_direction,
    'turn': level_playing_utils.get_random_turn,
    'fireZap': level_playing_utils.get_random_fire 
    }
}


def verbose_fn(unused_timestep, unused_player_index: int) -> None:
    pass


async def main():

    install_substrate("commons_harvest_language")
    observation = "WORLD.RGB"
    settings = {}
    verbose = False
    print_events = False

    # record TRUE makes the code to store agents observations as images
    record = False

    env_config = game.get_config()

    with config_dict.ConfigDict(env_config).unlocked() as env_config:
        roles = env_config.default_player_roles
        env_config.lab2d_settings = game.build(roles, env_config)
        #number_of_agents = env_config.lab2d_settings.get('numPlayers', 1)
    await level_playing_utils.run_episode(
        observation, settings, _ACTION_MAP,
        env_config, level_playing_utils.RenderType.PYGAME,
        verbose_fn=verbose_fn if verbose else None,
        print_events=print_events, record=record)


if __name__ == '__main__':
    asyncio.run(main())