# standard library imports
import pickle
import time

from rtgym import RealTimeGymInterface, DEFAULT_CONFIG_DICT, DummyRCDrone
from tmrl.util import partial, cached_property
from tmrl.envs import GenericGymEnv

# third-party imports
import keyboard
import numpy as np

# local imports
import tmrl.config.config_constants as cfg
from tmrl.custom.utils.tools import TM2020OpenPlanetClient, DualPlayerClient
import logging
from tmrl.networking import Server, RolloutWorker, Trainer

import csv

#set config params
PATH_REWARD = cfg.REWARD_PATH
DATASET_PATH = cfg.DATASET_PATH

my_config = DEFAULT_CONFIG_DICT.copy()
my_config["time_step_duration"] = 0.05
my_config["start_obs_capture"] = 0.05
my_config["time_step_timeout_factor"] = 1.0
my_config["ep_max_length"] = 100
my_config["act_buf_len"] = 8 #originally 4
my_config["reset_act_buf"] = False
my_config["benchmark"] = True
my_config["benchmark_polyak"] = 0.2

device = "cpu"
max_samples_per_episode = 1000
CRC_DEBUG = False

model_history = 10

# Set up Server & Worker                                    
security = None
password = cfg.PASSWORD

server_ip = '127.0.0.1' #"134.173.38.244"
server_port = 6666 #55555

#worker params
my_run_name = "tutorial"
weights_folder = cfg.WEIGHTS_FOLDER

model_path = str(weights_folder / (my_run_name + ".tmod"))
model_path_history = str(weights_folder / (my_run_name + "_"))

if __name__ == "__main__":
    my_server = Server(security=security, password=password, port=server_port)
    print("YAH BOIIIII")
print(__name__)

# Observation and action space:
env_cls = partial(GenericGymEnv, id="real-time-gym-v1", gym_kwargs={"config": my_config})

#compress samples to obs and rew
def my_sample_compressor(prev_act, obs, rew, terminated, truncated, info):
    prev_act_mod, obs_mod, rew_mod, terminated_mod, truncated_mod, info_mod = prev_act, obs, rew, terminated, truncated, info
    obs_mod = obs_mod[:4]  # here we remove the action buffer from observations
    return prev_act_mod, obs_mod, rew_mod, terminated_mod, truncated_mod, info_mod

sample_compressor = my_sample_compressor

#Memory
from tmrl.memory import TorchMemory
print("ENGINNNEERRRSSS")

class MyMemory(TorchMemory):
    def __init__(self,
                 act_buf_len=None,
                 device=None,
                 nb_steps=None,
                 sample_preprocessor: callable = None,
                 memory_size=1000000,
                 batch_size=32,
                 dataset_path=""):

        self.act_buf_len = act_buf_len  # length of the action buffer

        super().__init__(device=device,
                         nb_steps=nb_steps,
                         sample_preprocessor=sample_preprocessor,
                         memory_size=memory_size,
                         batch_size=batch_size,
                         dataset_path=dataset_path,
                         crc_debug=CRC_DEBUG)

    def __len__(self):
        if len(self.data) == 0:
            return 0  # self.data is empty
        result = len(self.data[0]) - self.act_buf_len - 1
        if result < 0:
            return 0  # not enough samples to reconstruct the action buffer
        else:
            return result  # we can reconstruct that many samples

#get human reward
def record_reward_dist(path_reward=PATH_REWARD):
    positions = []
    client = TM2020OpenPlanetClient()
    path = path_reward

    is_recording = False
    while True:
        if keyboard.is_pressed('r'):
            logging.info(f"start recording")
            is_recording = True
        if is_recording:
            data = client.retrieve_data(sleep_if_empty=0.01)  # we need many points to build a smooth curve
            terminated = bool(data[8])
            if keyboard.is_pressed('q') or terminated:
                logging.info(f"Computing reward function checkpoints from captured positions...")
                logging.info(f"Initial number of captured positions: {len(positions)}")
                positions = np.array(positions)

                final_positions = [positions[0]]
                dist_between_points = 0.1
                j = 1
                move_by = dist_between_points
                pt1 = final_positions[-1]
                while j < len(positions):
                    pt2 = positions[j]
                    pt, dst = line(pt1, pt2, move_by)
                    if pt is not None:  # a point was created
                        final_positions.append(pt)  # add the point to the list
                        move_by = dist_between_points
                        pt1 = pt
                    else:  # we passed pt2 without creating a new point
                        pt1 = pt2
                        j += 1
                        move_by = dst  # remaining distance

                final_positions = np.array(final_positions)
                logging.info(f"Final number of checkpoints in the reward function: {len(final_positions)}")

                pickle.dump(final_positions, open(path, "wb"))
                logging.info(f"All done")
                return
            else:
                positions.append([data[2], data[3], data[4]])
        else:
            time.sleep(0.05)  # waiting for user to press E

def record_human_data():
    logging.info(f"STARTEDDD")
    print("I started du, dum")
    client = DualPlayerClient()
    cycle = 0

    is_recording = False
    is_finished = False

    # data[0...N] = 0: Speed, 1: Distance, 2: x, 3:y, 4:z, 5: inputsteer, 6: inputgas, 7: engingercur, 8: rpm             
    with open('humanTrials.csv', 'a', newline='') as csvfile:
        fieldnames = ['H1_Speed', 'H1_Distance', 'H1_x_pos', 'H1_y_pos', 'H1_z_pos',  'H1_input_steer', 'H1_gas','H1_gear', 'H1_rpm', 'H2_Speed', 'H2_Distance', 'H2_x_pos', 'H2_y_pos', 'H2_z_pos',  'H2_input_steer', 'H2_gas','H2_gear', 'H2_rpm']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print("I made a csv dumb dumb")
        logging.info(f"MADE CSV")   

        while not is_finished:
            if keyboard.is_pressed('h'):
                logging.info(f"start recording")
                print("Started Biooottchchh")
                is_recording = True
            if keyboard.is_pressed('q'):
                logging.info(f"stop recording")
                is_recording = False
            if keyboard.is_pressed('c'):
                logging.info(f"completed recording and data saved!")
                is_recording = False
                is_finished = True
                return
            if is_recording:
                data = client.retrieve_data(sleep_if_empty=0.01)  # we need many points to build a smooth curve
                terminated = bool(data[16])
                writer.writerow({'H1_Speed' : data[0], 'H1_Distance' : data[1], 'H1_x_pos' : data[2], 'H1_y_pos' : data[3], 'H1_z_pos' : data[4],  'H1_input_steer' : data[5],
                    'H1_gas' : data[6], 'H1_gear' : data[7], 'H1_rpm' : data[8], 'H2_Speed' : data[9], 'H2_Distance' : data[10], 'H2_x_pos' : data[11], 'H2_y_pos' : data[12],
                    'H2_z_pos' : data[13],  'H2_input_steer' : data[14], 'H2_gas' : data[15], 'H2_gear' : data[16], 'H2_rpm' : data[17]})
            else:
                time.sleep(0.05)  # waiting for user to press E



if __name__ == "__main__":
    print("yee")
    record_human_data()

    #record_reward_dist(path_reward=PATH_REWARD)

    """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⣤⣤⣶⣦⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠙⠛⠛⠛⠛⠻⢿⣿⣷⣤⡀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠈⢻⣿⣿⡄⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⣸⣿⡏⠀⠀⠀⣠⣶⣾⣿⣿⣿⠿⠿⠿⢿⣿⣿⣿⣄⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⢰⣿⣿⣯⠁⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀ 
⠀⠀⣀⣤⣴⣶⣶⣿⡟⠀⠀⠀⢸⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⠀ 
⠀⢰⣿⡟⠋⠉⣹⣿⡇⠀⠀⠀⠘⣿⣿⣿⣿⣷⣦⣤⣤⣤⣶⣶⣶⣶⣿⣿⣿⠀ 
⠀⢸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀    <---- SUS 
⠀⣸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠉⠻⠿⣿⣿⣿⣿⡿⠿⠿⠛⢻⣿⡇⠀⠀ 
⠀⣿⣿⠁⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⠀⠀ 
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀ 
⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀ 
⠀⠀⠛⢿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⣰⣿⣿⣷⣶⣶⣶⣶⠶⠀⢠⣿⣿⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿⡏⠁⠀⠀⢸⣿⡇⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿⠁⠀⠈⠻⣿⣿⣿⣿⡿⠏⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

    """
