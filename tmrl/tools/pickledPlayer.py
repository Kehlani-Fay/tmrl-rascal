"""
Python class of example data I want to send over 
"""
import time
from tmrl.custom.utils.tools import DualPlayerClient

class HumanPickle():
    def __init__(self):
        self.start_time = time.time()
        self.client = DualPlayerClient()
        self.Hspeed, self.Hdistance, self.Hrpm, self.Rspeed, self.Rdistance, self.Rrpm = None, None, None, None, None, None
        self.Hxpos, self.Hypos, self.Hzpos, self.Rxpos, self.Rypos, self.Rzpos = None, None, None, None, None, None
        self.Hsteer, self.Hgas, self.Hgear, self.Htime, self.Rsteer, self.Rgas, self.Rgear, self.Rtime = None, None, None, None, None, None, None, None

    def send_data(self):
        data = self.client.retrieve_data(sleep_if_empty=0.01) 
        current_time = time.time() - self.start_time

        self.Hspeed, self.Hdistance, self.Hrpm, self.Rspeed, self.Rdistance, self.Rrpm = data[0], data[1], data[8], data[9], data[10], data[17]
        self.Hxpos, self.Hypos, self.Hzpos, self.Rxpos, self.Rypos, self.Rzpos =  data[2], data[3], data[4], data[11], data[12], data[13]
        self.Hsteer, self.Hgas, self.Hgear, self.Htime = data[5], data[6], data[7], current_time
        self.Rsteer, self.Rgas, self.Rgear, self.Rtime = data[14], data[15], data[16], current_time

if __name__ == "__main__":
    human_player = HumanPickle()
    human_player.send_data()
