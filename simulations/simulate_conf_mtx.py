import cmdstanpy

#From https://www.rpubs.com/dkarwosk12345/560307

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

import synthetic_matchups
from scipy.stats import pearsonr

def inv_logit(u):
    return 1 / (1 + np.exp(-u)) # NOTE: = np.exp(u) / (1 + np.exp(u))

def center(u):
    return u - np.mean(u)

""""
# parameters
K = 50
#underlying strengths of players
alpha = center(np.random.normal(size=K))

conferences = ["A", "B", "C", "D", "E"] * 10
# observations
N = K**2
#N = 1
player1 = np.empty(N, dtype=int)
player0 = np.empty(N, dtype=int)

for n in range(N):
    #Note: adjust K down one and then move it back up
    players = np.random.choice(np.arange(K), size=2, replace=False) # gets values from 0 to K-1 (because the interval is half open)
    player0[n] = players[0] + 1
    player1[n] = players[1] + 1

#NOTE: IMPORTANT
#do -1 to adjust down for the list we're pulling from
log_odds_player1 = alpha[player1 - 1] - alpha[player0 - 1]
prob_win_player1 = inv_logit(log_odds_player1)

#Most important line: How we create results
y = np.random.binomial(1, prob_win_player1) * 2 - 1

p0 = player0.tolist()
p1 = player1.tolist()
ylist = y.tolist()

# Prepare data for Stan model
mle_model_data = {
    "K": K,
    "N": N,
    "player0": p0, 
    "player1": p1,
    "y": ylist
}
"""

###################### PARAMETERS ######################

########### GENERATE MATCHUPS ########### 
teams_per_conference = 9
num_conferences = 22
conference_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V"]
conf_names = conference_names

full_teams = synthetic_matchups.generate_teams(conference_names, teams_per_conference)
full_conferences = [s[0] for s in full_teams]

K = len(full_teams)

#let's make a dict of all of the teams, arranged by conference
teams_dict = {}
for conf_name in conference_names:
    teams_dict[conf_name] = []

for i in range(len(full_conferences)):
    teams_dict[full_conferences[i]].append(full_teams[i])


#100% conference
#player_conf0, player_conf1 = synthetic_matchups.generate_conference_pairings(teams_dict, True)
#player0 = []
#player1 = []

# 50% conference

player0, player1 = synthetic_matchups.generate_random_pairings(teams_dict, 8)
player_conf0, player_conf1 = synthetic_matchups.generate_conference_pairings(teams_dict, False)


# 0% conference
"""
player0, player1 = synthetic_matchups.generate_random_pairings(teams_dict, 16)
player_conf0 = []
player_conf1 = []
"""

p0_names = player0 + player_conf0
p1_names = player1 + player_conf1
N = len(p0_names)
p0 = p0_names
p1 = p1_names

#Problem: We have a list of teams, we need a list of indexes that correspond to them, starting at 1
team_indexes_dict = {}
for i in range(K):
    team_indexes_dict[full_teams[i]] = i + 1

for i in range(N):
    p0[i] = team_indexes_dict[p0[i]]
    p1[i] = team_indexes_dict[p1[i]]
#Problem solved

########### END GENERATE MATCHUPS ########### 

########### GET ALPHAS ########### 
alpha = center(np.random.normal(size=K))

#### ADDING CONFERENCE BIASES (if needed) ####

alpha_conf_dict = {}
for conf_dict_element in conf_names:
    alpha_conf_dict[conf_dict_element] = np.random.normal(size=1)[0]

for alpha_element in range(K):
    alpha[alpha_element] = alpha[alpha_element] + alpha_conf_dict[full_conferences[alpha_element]]

## Center for Bayesian inference
alpha = center(alpha)


#True alpha rankings
a_r_ = np.flip(np.argsort(alpha)) #flip() so that alphas are descending
a_r_ = a_r_ + 1

conf_strengths = {}
##Get conference strengths ##
## SIM 2+ ##
for n in conf_names:
    conf_strengths[n] = 0

for i in range(K):
    conf_strengths[full_conferences[i]] = conf_strengths[full_conferences[i]] + alpha[i]

for g in conf_names:
    conf_strengths[g] = round(conf_strengths[g] / teams_per_conference, 4)

c_r_ = np.flip(np.argsort(np.array(list(conf_strengths.values()))))   
conf_strengths_ranking = [0] * num_conferences
#print(c_r_)
for ele in range(len(c_r_)):
    conf_strengths_ranking[c_r_[ele]] = ele + 1

conf_strengths_ranking = np.array(conf_strengths_ranking)
c_r_ = c_r_ + 1

#print(conf_strengths)
#print(conf_strengths_ranking)
##End get conference strengths (SIM2+) ##


#metrics like a_r_ return a list of the ranking of the teams
#NOT the ranking of the team at each index

#For example:
#We have teams 1, 2, 3
#With alphas 0.5, 0.4, 0.6
#Then a_r_ = [3, 1, 2]
#because 3 has the highest alpha, then 1, then 2

######### NOT  #########
#[2, 3, 1]
#Not 1 is ranked 2nd, 2 is ranked 3rd, 3 is ranked 1st
########################

########### END GET ALPHAS ########### 



###################### END PARAMETERS ######################



def calculate_btdm_simple_rank(model_data): 
    individual_model = cmdstanpy.CmdStanModel(stan_file="simplebtdm.stan")
    #The difference is that this generates a distribution, rather than just a 
    individual_posterior = individual_model.sample(data=model_data)

    # Compute posterior mean of alpha
    
    alpha_samples = individual_posterior.stan_variable("alpha")
    alpha_hat = np.mean(alpha_samples, axis=0)

    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=alpha, y=alpha_hat, s=50)
    plt.plot(alpha, alpha, color='green', linewidth=2)  # Green reference line
    plt.xlabel("True Alpha")
    plt.ylabel("Estimated Alpha Bayesian")
    plt.title("Bayesian Fit Plot")
    plt.show()
    """

    bt_r = individual_posterior.stan_variable(f'ranking')
    bt_r = np.mean(bt_r, axis=0)
    bt_r = np.argsort(bt_r)
    bt_r = bt_r + 1

    return bt_r, alpha_hat

def calculate_btdm_rank(model_data): 
    individual_model = cmdstanpy.CmdStanModel(stan_file="homebtdm.stan")
    #The difference is that this generates a distribution, rather than just a 
    individual_posterior = individual_model.sample(data=model_data)

    # Compute posterior mean of alpha
    
    alpha_samples = individual_posterior.stan_variable("alpha")
    alpha_hat = np.mean(alpha_samples, axis=0)

    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=alpha, y=alpha_hat, s=50)
    plt.plot(alpha, alpha, color='green', linewidth=2)  # Green reference line
    plt.xlabel("True Alpha")
    plt.ylabel("Estimated Alpha Bayesian")
    plt.title("Bayesian Fit Plot")
    plt.show()
    """

    bt_r = individual_posterior.stan_variable(f'ranking')
    bt_r = np.mean(bt_r, axis=0)
    bt_r = np.argsort(bt_r)
    bt_r = bt_r + 1

    return bt_r, alpha_hat

#Ok, now let's calculate RPI
from collections import defaultdict
def calculate_rpi(data):
    teams = set()
    records = defaultdict(lambda: {'wins': 0, 'games': 0, 'opponents': []})
    
    team_0 = data["player0"]
    team_1 = data["player1"]
    results = data["y"]


    # Process match results
    gm = 0
    for match in range(data["N"]):
        gm = gm + 1

        team1 = team_0[match]
        team2 = team_1[match] 
        result = results[match]

        teams.update([team1, team2])
        records[team1]['games'] += 1
        records[team2]['games'] += 1
        records[team1]['opponents'].append(team2)
        records[team2]['opponents'].append(team1)
        
        if result == -1:
            records[team1]['wins'] += 1
        elif result == 1:
            records[team2]['wins'] += 1
        else:
            records[team1]['wins'] += (1 / 3)
            records[team2]['wins'] += (1 / 3)
    
    # Compute WP
    wp = {team: (rec['wins'] / rec['games'] if rec['games'] > 0 else 0) for team, rec in records.items()}
    
    # Compute OWP
    owp = {}
    for team in teams:
        opponent_wps = []
        for opp in records[team]['opponents']:
            opp_record = records[opp]
            #if opp_record['games'] > 1:  # Exclude games against current team
            opp_wp = (opp_record['wins']) / (opp_record['games'])
            opponent_wps.append(opp_wp)
        owp[team] = sum(opponent_wps) / len(opponent_wps) if opponent_wps else 0
    
    # Compute OOWP
    oowp = {}
    for team in teams:
        opponent_owps = [owp[opp] for opp in records[team]['opponents'] if opp in owp]
        oowp[team] = sum(opponent_owps) / len(opponent_owps) if opponent_owps else 0


    #Compute bonus
    #TODO
    
    # Compute RPI
    rpi = {team: [0.25 * wp[team] + 0.50 * owp[team] + 0.25 * oowp[team], wp[team], owp[team], oowp[team]] for team in teams}
    #_wp = {team: wp[team] for team in teams}
    #_owp = {team: owp[team] for team in teams}
    #_oowp = {team: oowp[team] for team in teams}
    
    #return [rpi, _wp, _owp, _oowp]
    return rpi

import copy
def adjusted_rpi(data, rpis, rpi_ranks, neutrals):
    adjusted_rpis = copy.deepcopy(rpis)
    neutral_ = False

    team_0 = data["player0"]
    team_1 = data["player1"]
    results = data["y"]
    bonus = [0] * data["K"]
    #for each match in data
    for index in range(data["N"]):
        t0 = team_0[index] - 1
        t1 = team_1[index] - 1
        t0_rpi = rpi_ranks[t0]
        t1_rpi = rpi_ranks[t1]

        is_neutral = False

        if results[index] == 1: #home win
            if 1 <= t0_rpi <= 15:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0066
            elif 16 <= t0_rpi <= 30:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0056
            elif 31 <= t0_rpi <= 45:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0038
            elif 46 <= t0_rpi <= 60:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0018

            if 132 <= t1_rpi <= 146:
                if not is_neutral:
                    bonus[t0] = bonus[t0] - 0
                else:
                    bonus[t0] = bonus[t0] - 0.0018
            elif 147 <= t1_rpi <= 176:
                if not is_neutral:
                    bonus[t0] = bonus[t0] - 0.0032
                else:
                    bonus[t0] = bonus[t0] - 0.0042
            elif 177 <= t1_rpi:
                if not is_neutral:
                    bonus[t0] = bonus[t0] - 0.006
                else:
                    bonus[t0] = bonus[t0] - 0.0066





        elif results[index] == -1: #away win
            if 1 <= t1_rpi <= 15:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.007
                else:
                    bonus[t0] = bonus[t0] + 0.0066
            elif 16 <= t1_rpi <= 30:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.006
                else:
                    bonus[t0] = bonus[t0] + 0.0056
            elif 31 <= t1_rpi <= 45:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0042
                else:
                    bonus[t0] = bonus[t0] + 0.0038
            elif 46 <= t1_rpi <= 60:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0024
                else:
                    bonus[t0] = bonus[t0] + 0.0018
            elif 61 <= t1_rpi <= 75:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0011
                else:
                    bonus[t0] = bonus[t0] + 0


            if 132 <= t0_rpi <= 146:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.0038
                else:
                    bonus[t1] = bonus[t1] - 0.0018
            elif 147 <= t0_rpi <= 176:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.0052
                else:
                    bonus[t1] = bonus[t1] - 0.0042
            elif 177 <= t0_rpi:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.007
                else:
                    bonus[t1] = bonus[t1] - 0.0066




        else: #tie
            if 1 <= t1_rpi <= 15:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0052
                else:
                    bonus[t0] = bonus[t0] + 0.0046
            elif 16 <= t1_rpi <= 30:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0032
                else:
                    bonus[t0] = bonus[t0] + 0.0028
            elif 31 <= t1_rpi <= 45:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0014
                else:
                    bonus[t0] = bonus[t0] + 0.0008
            elif 46 <= t1_rpi <= 60:
                if not is_neutral:
                    bonus[t0] = bonus[t0] + 0.0004
                else:
                    bonus[t0] = bonus[t0] + 0
            elif 147 <= t1_rpi <= 176:
                if not is_neutral:
                    bonus[t0] = bonus[t0] - 0
                else:
                    bonus[t0] = bonus[t0] - 0.0024
            elif 177 <= t1_rpi:
                if not is_neutral:
                    bonus[t0] = bonus[t0] - 0.0046
                else:
                    bonus[t0] = bonus[t0] - 0.0056




            if 1 <= t0_rpi <= 15:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0046
            elif 16 <= t0_rpi <= 30:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0028
            elif 31 <= t0_rpi <= 45:
                if not is_neutral:
                    bonus[t1] = bonus[t1] + 0
                else:
                    bonus[t1] = bonus[t1] + 0.0008
            elif 132 <= t0_rpi <= 146:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.0014
                else:
                    bonus[t1] = bonus[t1] - 0
            elif 147 <= t0_rpi <= 176:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.0028
                else:
                    bonus[t1] = bonus[t1] - 0.0024
            elif 177 <= t0_rpi:
                if not is_neutral:
                    bonus[t1] = bonus[t1] - 0.0063
                else:
                    bonus[t1] = bonus[t1] - 0.0056

    #for each team
    #check if it qualifies for a bonus by checking the rpi_rank of the other team
    #if so, then add/subtract the bonus to the corresponding adjusted_rpis
    #return adjusted_rpis
    #list(map(lambda a, b: a + b, list1, list2))
    #adjusted_rpis = adjusted_rpis + bonus
    adjusted_rpis = list(map(lambda a, b: a + b, adjusted_rpis, bonus))
    return adjusted_rpis


#Group-wise mean rank error
def atdr (truth, metric, conf):
    size = len(conf) # = K
    truth_pos = [0] * size
    metric_pos = [0] * size

    conf_score = {}
    conf_teams = {}
    for index in range(size):
        truth_pos[truth[index] - 1] = index + 1
        metric_pos[metric[index] - 1] = index + 1

    for index in range(size):
        #estimated rank - true rank
        diff = metric_pos[index] - truth_pos[index]
        if conf[index] in conf_score:
            conf_score[conf[index]] = conf_score[conf[index]] + diff
            conf_teams[conf[index]] = conf_teams[conf[index]] + 1
        else:
            conf_score[conf[index]] = diff
            conf_teams[conf[index]] = 1

    for key in conf_score:
        conf_score[key] = round(conf_score[key] / conf_teams[key], 4)

    return conf_score


def spearman (truth, metric, conf):
    size = len(conf)
    truth_pos = [0] * size
    metric_pos = [0] * size

    for index in range(size): #ranks
        truth_pos[truth[index] - 1] = index + 1
        metric_pos[metric[index] - 1] = index + 1


    total_diff = 0
    for index in range(size):
        diff = metric_pos[index] - truth_pos[index]
        total_diff = total_diff + diff**2
    
    sc = 1 - (6 * total_diff / (size * (size**2 - 1)))
    return sc

def confusion_matrix(ranking_list, simulation_data):
    p0_ = np.array(simulation_data["player0"])
    p1_ = np.array(simulation_data["player1"])
    y_ = simulation_data["y"]

    y_predicted = []
    #print(p0_)
    #print(ranking_list)
    for tm_index in range(len(p1_)):
        index_diff = np.where(ranking_list == p0_[tm_index])[0][0] - np.where(ranking_list == p1_[tm_index])[0][0]
        y_predicted.append(round(index_diff / abs(index_diff)))
    
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for game in range(len(y_)):
        true_res = y_[game]
        pred_res = y_predicted[game]

        #Note: If tie, don't do anything
        if true_res != 0:
            if true_res == pred_res:
                #home team won, predicted
                if true_res == 1:
                    tp = tp + 1
                else:
                    tn = tn + 1
            else:
                if true_res == -1:
                    fp = fp + 1
                else:
                    fn = fn + 1

    sample_accuracy = (tp + tn) / (tp + tn + fp + fn)
    sample_precision = tp / (tp + fp)
    sample_recall = tp / (tp + fn)
    sample_f1 = 2 * (sample_precision * sample_recall) / (sample_precision + sample_recall)

    return [sample_accuracy, sample_precision, sample_recall, sample_f1]



########### RUN SIMULATIONS ########### 
num_simulations = 10


bt_er_ = [0] * num_simulations
rpi_er_ = [0] * num_simulations

#contains the results from all the simulations
bt_r_s = [0] * num_simulations
rpi_r_s = [0] * num_simulations

btdm_rank_error = 0 
rpi_rank_error = 0

bt_spearmans = [0] * num_simulations
rpi_spearmans = [0] * num_simulations

bt_confusion = [0] * num_simulations
rpi_confusion = [0] * num_simulations

for sim in range(num_simulations):


    ########### GENERATE GAME RESULTS ########### 

    ##Deterministic Generation ##
    """
    ## SIM1 ##
    ylist = []
    for tm_index in range(len(p1)):
        index_diff = np.where(a_r_ == p0[tm_index])[0][0] - np.where(a_r_ == p1[tm_index])[0][0]
        ylist.append(round(index_diff / abs(index_diff)))

    ##Get conference strengths ##
    for n in conf_names:
        conf_strengths[n] = 0

    for i in range(K):
        conf_strengths[full_conferences[i]] = conf_strengths[full_conferences[i]] + (K - np.where(a_r_ == i + 1)[0][0])

    for g in conf_names:
        conf_strengths[g] = round(conf_strengths[g] / teams_per_conference, 4)
    ##End get conference strengths ##
    ## END SIM1 ##
    """

    """
    ## RANDOM GENERATION
    ## SIM2 ##
    ylist = []
    for tm_index in range(len(p1)):
        ylist.append(random.randint(-1, 1))
    ##Get conference strengths -- no special code needed
    ## Note: even though the results are completely random, alpha is still used to determine the best conference
    ## END SIM2 ##
    """
    """
    ## SIM3-4 ##    
    ## Simple BT Generation ##
    
    #do -1 to adjust down for the list we're pulling from (index starting at 0, rather than 1)
    log_odds_player1 = alpha[np.array(p1) - 1] - alpha[np.array(p0) - 1]
    prob_win_player1 = inv_logit(log_odds_player1)

    # Generate results
    # Only win/loss
    y = np.random.binomial(1, prob_win_player1) * 2 - 1
    ylist = y.tolist()
    
    ## END SIM3-4 ##  
    """
    ## SIM5-8 ##    
    ## BT Generation With Ties ##

    #home_advantage_coeff = 0 # 0 = ln(1)
    home_advantage_coeff = np.log(2) # = ln(2)
    tie_coeff = 0 #0 = ln(1)
    #do -1 to adjust down for the list we're pulling from (index starting at 0, rather than 1)
    numerator_player1 = np.exp(home_advantage_coeff + alpha[np.array(p1) - 1])
    numerator_player0 = np.exp(alpha[np.array(p0) - 1])
    numerator_tie = np.exp(tie_coeff + 0.5 * (alpha[np.array(p1) - 1] + alpha[np.array(p0) - 1]))
    denom = numerator_player0 + numerator_player1 + numerator_tie
    #now
    prob_win_p1 = numerator_player1 / denom
    prob_win_p0 = numerator_player0 / denom
    prob_tie = numerator_tie / denom

    # Generate results
    # Only win/loss
    #y = np.random.binomial(1, prob_win_player1) * 2 - 1
    y = [np.random.choice([-1, 0, 1], p=[prob_win_p0[elem], prob_tie[elem], prob_win_p1[elem]]) for elem in range(len(prob_win_p0))]
    ylist = y
    
    ## END SIM3-4 ##  

    ########### END GENERATE GAME RESULTS ########### 







    ########### SIMULATION DATA ########### 
    sim_data = {
        "K": K,
        "N": N,
        "player0": p0, 
        "player1": p1,
        "y": ylist
    }

    ### Calculate RPI ###
    ### Simple Model (no home advantage)
    #bt_r_s[sim], alpha_hat = calculate_btdm_simple_rank(sim_data)

    ### Advanced model (With home advantage)
    bt_r_s[sim], alpha_hat = calculate_btdm_rank(sim_data)

    bt_er_[sim] = list(atdr(a_r_, bt_r_s[sim], full_conferences).values())
    bt_spearmans[sim] = spearman(a_r_, bt_r_s[sim], full_conferences)
    ### End Calculate RPI ###


    ### Calculate RPI ###
    rpi_full_values = calculate_rpi(sim_data)
    rpi_values = [value[0] for value in rpi_full_values.values()]
    #turn into a numpy array for sorting function
    rpi_values_np = np.array(rpi_values)
    rpi_r_s[sim] = np.flip(np.argsort(rpi_values_np))
    rpi_r_s[sim] = rpi_r_s[sim] + 1

    ### Adjusted RPI (if needed) ###
    #"""
    adjusted_rpi_values = adjusted_rpi(sim_data, rpi_values, rpi_r_s[sim], [])
    rpi_values_np = np.array(adjusted_rpi_values)
    rpi_r_s[sim] = np.flip(np.argsort(rpi_values_np))
    rpi_r_s[sim] = rpi_r_s[sim] + 1
    #"""

    rpi_er_[sim] = list(atdr(a_r_, rpi_r_s[sim], full_conferences).values())
    rpi_spearmans[sim] = spearman(a_r_, rpi_r_s[sim], full_conferences)

    bt_confusion[sim] = confusion_matrix(bt_r_s[sim], sim_data)
    rpi_confusion[sim] = confusion_matrix(rpi_r_s[sim], sim_data)

    #################################

np_bt_er_ = np.array(bt_er_)
np_rpi_er_ = np.array(rpi_er_)

np_bt_confusion = np.array(bt_confusion)
np_rpi_confusion = np.array(rpi_confusion)


########### END RUN SIMULATIONS ########### 




########### PRINT SIMULATIONS OUTPUT ########### 

var_rank_error_conf_list_btdm = []
avg_var_sim_btdm = 0

var_rank_error_conf_list_rpi = []
avg_var_sim_rpi = 0

#print("Away teams (matchups)")
#print(mle_model_data["player0"])
#print("Home teams (matchups)")
#print(mle_model_data["player1"])
"""
print("Conference names")
print(conf_names)
print("True Team Rankings (best to worst)")
print([full_teams[elem - 1] for elem in a_r_])"
"""
print("Average Conference Strength Parameters (if applicable)")
print(conf_strengths)
print("Number of season simulations")
print(num_simulations)
print("")

btdm_rank_error = np.mean(np_bt_er_, axis=0)
rpi_rank_error = np.mean(np_rpi_er_, axis=0)

"""
print("Rank error for BTDM by conference (averaged) (+ values = underestimation (ranked lower than true value))")
btdm_rank_error = np.mean(np_bt_er_, axis=0)
print([round(num, 4) for num in btdm_rank_error])
print("Variance of above BTDM rank error averages")
print(round(np.var(btdm_rank_error), 4))
print("Variance in BTDM rank error over the simulations, by each conference")
var_rank_error_conf_list_btdm = np.var(np_bt_er_, axis=0)
print([round(num, 4) for num in var_rank_error_conf_list_btdm])
print("Average variance in BTDM rank error of each simulation")
avg_var_sim_btdm = np.mean(np.var(np_bt_er_, axis=1))
print(round(avg_var_sim_btdm, 4))
print("Average spearman's coefficient for BTDM rankings, compared to ground truth")
print(round(sum(bt_spearmans) / num_simulations, 4))
print("Variance of above BTDM spearman's coefficient")
print(round(np.var(bt_spearmans), 4))
print("Correlation coefficient (R) between conference strength and BTDM rank error")
print("-1 = better conferences are overestimated")
print("(+1 = better conferences are underestimated)")
r_btdm, p_btdm = pearsonr(list(conf_strengths.values()), btdm_rank_error)
print(round(r_btdm, 4))
print("P-value for correlation between conference strength and BTDM rank error")
print(round(p_btdm, 4))

print("Rank error for RPI by conference (averaged)")
rpi_rank_error = np.mean(np_rpi_er_, axis=0)
print([round(num, 4) for num in rpi_rank_error])
print("Variance of above RPI rank error averages")
print(round(np.var(rpi_rank_error), 4))
print("Variance in RPI rank error over the simulations, by each conference")
var_rank_error_conf_list_rpi = np.var(np_rpi_er_, axis=0)
print([round(num, 4) for num in var_rank_error_conf_list_rpi])
print("Average variance in RPI rank error of each simulation")
avg_var_sim_rpi = np.mean(np.var(np_rpi_er_, axis=1))
print(round(avg_var_sim_rpi, 4))
print("Average spearman's coefficient for RPI rankings, compared to ground truth")
print(round(sum(rpi_spearmans) / num_simulations, 4))
print("Variance of above RPI spearman's coefficient")
print(round(np.var(rpi_spearmans), 4))
print("Correlation coefficient (R) between conference strength and RPI rank error")
r_rpi, p_rpi = pearsonr(list(conf_strengths.values()), rpi_rank_error)
print(round(r_rpi, 4))
print("P-value for correlation between conference strength and RPI rank error")
print(round(p_rpi, 4))
"""

print("Average spearman's coefficient for BTDM rankings, compared to ground truth")
print(round(sum(bt_spearmans) / num_simulations, 4))
print("Average spearman's coefficient for RPI rankings, compared to ground truth")
print(round(sum(rpi_spearmans) / num_simulations, 4))

print("")



print("Correlation coefficient (R) between conference strength and RPI rank error - BTDM rank error")
r_rpi, p_rpi = pearsonr(list(conf_strengths.values()), [rpi_rank_error[elem] - btdm_rank_error[elem] for elem in range(len(rpi_rank_error))])
print(round(r_rpi, 4))
print("P-value for correlation between conference strength and RPI rank error - BTDM rank error")
print(round(p_rpi, 4))

print("Average BT Accuracy")
print(np.mean(np_bt_confusion[:, 0]))
print("Variance of BT Accuracy")
print(np.var(np_bt_confusion[:, 0]))
print("Average BT Precision")
print(np.mean(np_bt_confusion[:, 1]))
print("Variance of BT Precision")
print(np.var(np_bt_confusion[:, 1]))
print("Average BT Recall")
print(np.mean(np_bt_confusion[:, 2]))
print("Variance of BT Recall")
print(np.var(np_bt_confusion[:, 2]))
print("Average BT F1")
print(np.mean(np_bt_confusion[:, 3]))
print("Variance of BT F1")
print(np.var(np_bt_confusion[:, 3]))

print("")

print("Average RPI Accuracy")
print(np.mean(np_rpi_confusion[:, 0]))
print("Variance of RPI Accuracy")
print(np.var(np_rpi_confusion[:, 0]))
print("Average RPI Precision")
print(np.mean(np_rpi_confusion[:, 1]))
print("Variance of RPI Precision")
print(np.var(np_rpi_confusion[:, 1]))
print("Average RPI Recall")
print(np.mean(np_rpi_confusion[:, 2]))
print("Variance of RPI Recall")
print(np.var(np_rpi_confusion[:, 2]))
print("Average RPI F1")
print(np.mean(np_rpi_confusion[:, 3]))
print("Variance of RPI F1")
print(np.var(np_rpi_confusion[:, 3]))





