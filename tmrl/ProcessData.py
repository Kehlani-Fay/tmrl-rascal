"""
Inverse learn collected human data for approximate reward function
"""
import glob
import pandas as pd
import numpy as np
import math 
import random
from scipy.stats import norm

def determine_risk(df, race_rewards, is_H1):

    iters = 0
    risk_H1 = []
    risk_H2 = []

    #prob of collision given the last observation and the action taken
    for row in df:
        #take every player position at time t 
        delta_t = .008

        #risk = 1/1 - c integral (-1, VAR 95%) (reward_race)(prob of return)

        if(is_H1 == True):
            prior_vel = row["H1_vel"]
            prior_x = row["H1_x_pos"]
            prior_y = row["H1_y_pos"]
            current_x = next_row["H1_x_pos"]
            current_y = next_row["H1_y_pos"]
            self_x = next_row["H2_x_pos"]
            self_y = next_row["H2_y_pos"]
            self_vel = next_row["H2_vel"]

        else:
            prior_vel = row["H2_vel"]
            prior_x = row["H2_x_pos"]
            prior_y = row["H2_y_pos"]
            self_x = next_row["H2_x_pos"]
            self_y = next_row["H2_y_pos"]
            self_vel = next_row["H2_vel"]
        
        #calculate p(x)
        guassian_x = prior_x + prior_vel * delta_t
        guassian_y = prior_y + prior_vel * delta_t

        #sample prob to get percent chance

        probability_pdf_x = norm.pdf(self_x, loc=guassian_x, scale=1.0)
        probability_pdf_y = norm.pdf(self_y, loc=guassian_y, scale=1.0)

        p_x_return = probability_pdf_x * probability_pdf_y
        risk_alpha = .95 #also called CVAR alpha
        x = race_rewards[iters]
        value_invested = 1
        var =  np.percentile(x, 100 * (1-risk_alpha)) * value_invested

        portfolio_returns = race_rewards
        
        # Get back to a return rather than an absolute loss
        var_pct_loss = var / value_invested
        
        cvar = value_invested * np.nanmean(portfolio_returns[portfolio_returns < var_pct_loss])                                             
        iters += 1
        risk_H1.append(cvar)
        risk_H1.append(cvar)

        return cvar

def get_centerline():

    #read from centerline csv outine of course
    pd_left = pd.read_csv("left_wall.csv", low_memory=False)
    pd_right = pd.read_csv("right_wall.csv", low_memory=False)
    centerline_left_x = pd_left['wall_outline_x'].values[0]
    centerline_left_y = pd_left['wall_outline_y'].values[0]
    centerline_right_x = pd_right['wall_outline_x'].values[0]
    centerline_right_y = pd_right['wall_outline_y'].values[0]
    centerline_up_z = pd_right['wall_outline_z_up'].values[0]
    centerline_down_z = pd_right['wall_outline_z_down'].values[0]

    centerline_points = np.zeros(shape = (centerline_left_x.size, centerline_left_y.size, centerline_down_z.size))

    #get centerline
    for val in range(0, centerline_left_x.size):
        left_x = centerline_left_x[val]
        left_y = centerline_left_y[val]
        right_x = centerline_right_x[val]
        right_y = centerline_right_y[val]
        up_z = centerline_up_z[val]
        down_z = centerline_down_z[val]
        dist_x = abs(left_x - right_x) / 2
        dist_y = abs(left_y - right_y) / 2
        dist_z = abs(down_z - up_z) / 2

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

        centerline_points[val] = [(total_dist_x, total_dist_y, dist_z)]
    return centerline_points
    
def evaluate_risk(df, centerline_points):

    abs_time = 0
    H1_reward_points = []
    H2_reward_points = []

    for row in df:         
        #H1_x_pos,H1_y_pos,H1_z_pos
        H1_x_pos = df["H1_x_pos"][row]
        H1_y_pos = df["H1_y_pos"][row]
        H1_z_pos = df["H1_z_pos"][row]

        H2_x_pos = df["H2_x_pos"][row]
        H2_y_pos = df["H2_y_pos"][row]
        H2_z_pos = df["H2_z_pos"][row]

        H1_reward_total_time = df["H1_time"][row]
        H2_reward_total_time = df["H2_time"][row]

        closest_H1 = None
        closest_centerline_dist_H1 = 99999999999

        closest_H2 = None
        closest_centerline_dist_H2 = 99999999999

        #for data in csv, get current closest distance from centerline 
        for tup in centerline_points:
            centerline_x, centerline_y, centerline_z = tup

            dist_H1 = math.sqrt(centerline_x - H1_x_pos)**2 + (centerline_y - H1_y_pos)**2 + (centerline_z - H1_z_pos)**2
            dist_H2 = math.sqrt(centerline_x - H2_x_pos)**2 + (centerline_y - H2_y_pos)**2 + (centerline_z - H2_z_pos)**2

            if(closest_H1 == None):
                closest_H1 = tup
                closest_H2 = tup
                closest_centerline_dist_H1 = dist_H1
                closest_centerline_dist_H2 = dist_H2

            if(closest_centerline_dist_H1 > dist_H1):
                closest_H1 = tup
                closest_centerline_dist_H1 = dist_H1

            if(closest_centerline_dist_H2 > dist_H2):
                closest_H2 = tup
                closest_centerline_dist_H2 = dist_H2
        
        H1_reward_points.append(closest_H1)
        H2_reward_points.append(closest_H2)

    #set reward_race as centerline displacement from start
    H1_reward = 0
    H2_reward = 0

    total_displacement_x = 0
    total_displacement_y = 0
    total_displacement_z = 0

    #get total displacement of the track
    prior_x, prior_y, prior_z = 0,0,0
    for val in range(0, len(centerline_points)):
        centerline_x, centerline_y, centerline_z = tup

        total_displacement_x += centerline_x - prior_x
        total_displacement_y += centerline_y - prior_y
        total_displacement_z += centerline_z - prior_z

        prior_x, prior_y, prior_z = centerline_x, centerline_y, centerline_z

    #get reward by percent increase covered by track / percent track
    H1_reward = 0.0
    prior_percent = 0.0
    for reward_point in H1_reward_points:
        index_centerline = centerline_points.index(reward_point)
        num_centerline_points = len(centerline_points)

        #percent of the way done through track 
        percent_through = index_centerline / num_centerline_points

        #time 
        abs_time += .008 #dt for each recorded time step\
        H1_reward += (percent_through - prior_percent)/.008 * (1/H1_reward_total_time * 10)

        prior_percent = percent_through

    H2_prior_percent = 0.0
    H2_reward = 0.0

    for reward_point in H2_reward_points:
        index_centerline = centerline_points.index(reward_point)
        num_centerline_points = len(centerline_points)

        #percent of the way done through track 
        percent_through = index_centerline / num_centerline_points

        #time 
        abs_time += .008 #dt for each recorded time step\
        H2_reward += (percent_through - H2_prior_percent)/.008 * (1/H2_reward_total_time * 10)

        prior_percent = percent_through

    reward_race = (H1_reward, H2_reward)

    #reward_human = reward_race - reward_risk
    return reward_race

def determine_alpha(risk_reward):
    delta = 0

    for i in range(len(risk_reward) - 1):
        old_risk = risk_reward[i]
        current_risk = risk_reward[i + 1]

        delta += current_risk - old_risk

def main():
    #read optimal reward
    determined_centerline = get_centerline()

    #read human reward
    glued_data = pd.DataFrame()
    for file_name in glob.glob("/home/hal9000/Projects/tmrl-rascal/tmrl/Human-Data/CSVs/"+'*.csv'):
        df = pd.read_csv(file_name, low_memory=False)
        glued_data = pd.concat([glued_data,df],axis=0) #all data 

        evaluate_risk(df)

    for file_name in glob.glob("/home/hal9000/Projects/tmrl-rascal/tmrl/Human-Data/CSVs/"+'*.csv'):
        df = pd.read_csv(file_name, low_memory=False)
        glued_data = pd.concat([glued_data,df],axis=0) #all data 
        determine_risk(df)
        determine_alpha(df)

        #reward risk = 

if __name__ == "__main__":
    main()