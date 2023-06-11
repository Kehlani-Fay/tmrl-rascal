"""
Inverse learn collected human data for approximate reward function
"""
import glob
import pandas as pd
import numpy as np

def get_centerline():
    #read from centerline csv outine of course
    pd_left = pd.read_csv("left_wall", low_memory=False)
    pd_right = pd.read_csv("right_wall", low_memory=False)
    centerline_left_x = pd_left['wall_outline_x'].values[0]
    centerline_left_y = pd_left['wall_outline_y'].values[0]
    centerline_right_x = pd_right['wall_outline_x'].values[0]
    centerline_right_y = pd_right['wall_outline_y'].values[0]
    centerline_points = np.zeros(shape = (centerline_left_x.size, centerline_left_y.size))

    #get centerline
    for val in range(0, centerline_left_x.size):
        left_x = centerline_left_x[val]
        left_y = centerline_left_y[val]
        right_x = centerline_right_x[val]
        right_y = centerline_right_y[val]
        dist_x = abs(left_x - right_x) / 2
        dist_y = abs(left_y - right_y) / 2

        order_x = (right_x - left_x) > 0
        order_y = (right_y - left_y) > 0

        #based on direction of turns, find centerline
        if(order_x):
            if(order_y): #default
                total_dist_x = dist_x + left_x
                total_dist_y = dist_y + left_y
            else: #right turn
                total_dist_x = dist_x + left_x
                total_dist_y = dist_y - left_y
        else:
            if(order_y): #reverse
                total_dist_x = dist_x + right_x
                total_dist_y = dist_y + right_y
            else: #left turn
                total_dist_x = dist_x + right_x
                total_dist_y = dist_y - right_y

        centerline_points[val] = [(total_dist_x, total_dist_y)]
    return centerline_points
    
def evaluate_risk(df, centerline_points):
    abs_time = 0
    #for data in csv, get current closest distance from centerline 
    abs_time += 10
    #set reward_race as centerline displacement from start

    #reward_human = reward_race - reward_risk
    return reward_human

def determine_risk(df, centerline_points):
    #take every player position at time t 
    #state and velocity buckets 
    #write to dataset: position/velo bucket, reward
    #risk = 1/1 - c integral (-1, VAR 95%) (reward_race)(prob of return)
    #return risk of every bucket

def determine_alpha(df):
    #average rate of change 
    #risk_level of action - prior action * scale_factor

def main():
    #read optimal reward

    #read human reward
    glued_data = pd.DataFrame()
    for file_name in glob.glob("/home/hal9000/Projects/tmrl-rascal/tmrl/Human-Data/CSVs/"+'*.csv'):
        df = pd.read_csv(file_name, low_memory=False)
        glued_data = pd.concat([glued_data,x],axis=0) #all data 

        evaluate_risk(df)

    for file_name in glob.glob("/home/hal9000/Projects/tmrl-rascal/tmrl/Human-Data/CSVs/"+'*.csv'):
        df = pd.read_csv(file_name, low_memory=False)
        glued_data = pd.concat([glued_data,df],axis=0) #all data 
        determine_risk(df)
        determine_alpha(df)


if __name__ == "__main__":
    main()