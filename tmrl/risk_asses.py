#tut: https://www.quantrocket.com/code/?repo=quant-finance-lectures&path=%2Fcodeload%2Fquant-finance-lectures%2Fquant_finance_lectures%2FLecture40-VaR-and-CVaR.ipynb.html

import numpy as np
import pandas as pd

from scipy.stats import norm
import time
import math 
import matplotlib.pyplot as plt

def value_at_risk(prior_rewards, rewards, alpha, index, lookback, weights):
    value_invested = 1
    # Multiply asset returns by weights to get one weighted portfolio return
    portfolio_returns = rewards[(index-lookback):index]

    print(portfolio_returns)
    portfolio_returns = portfolio_returns.astype(np.float)
    portfolio_returns = portfolio_returns - prior_rewards


    # Compute the correct percentile loss and multiply by value invested
    var = np.percentile(portfolio_returns, [100 * (1-alpha)]) * value_invested
    return var

def cvar(value_invested, prior_rewards, rewards, weights, alpha, index, lookback):
    # Call out to our existing function
    var = value_at_risk(prior_rewards, rewards, alpha, index, lookback, weights) #indx

    portfolio_returns = rewards[(index-lookback):index]
    portfolio_returns = portfolio_returns.astype(np.float)
    portfolio_returns = portfolio_returns - prior_rewards

    # Get back to a return rather than an absolute loss
    var_pct_loss = var / value_invested

    return value_invested * np.nanmean(portfolio_returns[portfolio_returns < var_pct_loss])

def main():
    df = pd.read_csv('/home/hal9000/Projects/tmrl-rascal/tmrl/Human-Data/CSVs/humanTrialsName=JasperTia3.csv', skiprows=[1, 2])
    df.iloc[::5, :]
    rewards = df['H1_Distance'].values
    risk_reward_dict = {}

    #relative distance
    h1_x = df['H1_x_pos'].values
    h1_y = df['H1_y_pos'].values

    h2_x = df['H2_z_pos'].values
    h2_y = df['H2_input_steer'].values

    rel_dist_x = abs(h1_x - h2_x)
    rel_dist_y = abs(h1_y - h2_y)
    euclidian = abs(rel_dist_x ** 2 + rel_dist_y**2)
    rel_dist = np.zeros(len(euclidian))

    for val in euclidian:
        np.append(rel_dist, math.sqrt(val))

    value_invested = 1.0
    h1_risk_values = []
    h1_rewards = []
    h2_risk_values = []
    h2_rewards = []
    risk_alpha = .95

    #print(rewards)
    lookback = 200
    prior_rewards = np.zeros(lookback)
    for ind in range(lookback, len(rewards)):
        weights = rel_dist[(ind-lookback):ind]
        cvar_risk = cvar(value_invested, prior_rewards, rewards, weights, risk_alpha, ind, lookback)
        prior_rewards = rewards[(ind-lookback):ind]
        h1_risk_values.append(cvar_risk)
        h1_rewards.append(rewards[ind])

    print("completed h1")
    rewards = df['H2_y_pos'].values
    #print(rewards)
    prior_rewards = np.zeros(lookback)
    for ind in range(lookback, len(rewards)):
        weights = rel_dist[(ind-lookback):ind]
        cvar_risk = cvar(value_invested, prior_rewards, rewards, weights, risk_alpha, ind, lookback)
        prior_rewards = rewards[(ind-lookback):ind]
        h2_risk_values.append(cvar_risk)
        h2_rewards.append(rewards[ind])

    print("Now returning cvar risk and rewards")
    risk_reward_dict[0] = (h1_rewards,h1_risk_values)
    risk_reward_dict[1] = (h2_rewards,h2_risk_values)
    #print(h1_risk_values)
    #print(h1_rewards)
    #print()

    #print("H2")
    #print(h2_risk_values)

    plt.plot(h1_risk_values)
    plt.plot(h2_risk_values)
    plt.legend("human", "robot")
    plt.xlabel("time steps")
    plt.ylabel("CVAR level")
    plt.show()

    #print(h2_rewards)

if __name__ == "__main__":
    main()

#1) feed encoder into SAC
#2) Test encoder input outputs 
#3) Train