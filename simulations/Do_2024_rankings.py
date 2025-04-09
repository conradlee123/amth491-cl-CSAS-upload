test_rpi_triples = [(0.25, 0.3, 0.45), 
                    (0.3, 0.25, 0.45), 
                    (0.3, 0.3, 0.4),  
                    (0.35, 0.35, 0.3), 
                    (0.4, 0.35, 0.25),
                    (0.45, 0.4, 0.15)]

len_triples = len(test_rpi_triples)


import cmdstanpy
import csv

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


def sum_to_1_triples():
    solutions = []

    for x in range(21):  # x can be from 0 to 100
        for y in range(21 - x):  # y can be from 0 to (100 - x)
            z = 20 - x - y  # Compute z
            if z >= 0:  # Ensure z is nonnegative
                solutions.append((x / 20, y / 20, z / 20))  # Store the solution

    return solutions  # Output the list of solutions

rpi_triples = sum_to_1_triples()

modified_rpi_triples = rpi_triples
len_triples = len(modified_rpi_triples)

modified_rpi_triples = [(0.25, 0.5, 0.25), (0.15, 0.3, 0.55)]
len_triples = len(modified_rpi_triples)

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
"""
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
#player0, player1 = synthetic_matchups.generate_random_pairings(teams_dict, 16)
#player_conf0 = []
#player_conf1 = []
"""

p0_names = player0 + player_conf0
p1_names = player1 + player_conf1
N = len(p0_names)
p0 = p0_names
p1 = p1_names

"""
####### END SYNTHETIC GENERATION

#TODO
# Read in the data
season_data_2024_raw = []
with open("scores_final_neutrals.csv", mode="r", newline="") as file_csv:
    reader = csv.reader(file_csv)

    rowNum = 0
    # Make it 1 big 2D array
    for row in reader:
        season_data_2024_raw.append(row)

season_data_2024_header = season_data_2024_raw[0]
season_data_2024_raw = season_data_2024_raw[1:]

# Get all of the D1 Teams
teams_2024_games_played = {}
for row in season_data_2024_raw:
    if row[1] in teams_2024_games_played:
        teams_2024_games_played[row[1]] = teams_2024_games_played[row[1]] + 1
    else:
        teams_2024_games_played[row[1]] = 1

    if row[4] in teams_2024_games_played:
        teams_2024_games_played[row[4]] = teams_2024_games_played[row[4]] + 1
    else:
        teams_2024_games_played[row[4]] = 1

#print(teams_2024_games_played)

# Remove matches with teams that are not in D1 (for RPI)
full_teams_thresh = []
for team in teams_2024_games_played.keys():
    if teams_2024_games_played[team] > 5:
        full_teams_thresh.append(team)

#print(full_teams)
season_data_2024 = []
for row in season_data_2024_raw:
        
    if (row[1] in full_teams_thresh) and (row[4] in full_teams_thresh):
    #if 1 == 1:
        season_data_2024.append(row)

# Get all of the D1 conferences
full_teams = []
full_conferences = []
conference_names = []

p0 = []
p1 = []

#UMass, ex-- what is a neutral game
neutral_field = []

y_l = []

for row in season_data_2024:
    #away team
    p0.append(row[4])
    #home team
    p1.append(row[1])

    y_l.append(int(row[7]))

    #neutral field
    neutral_field.append(int(row[8]))
    #neutral_field.append(0)


    if row[1] not in full_teams:
        full_teams.append(row[1])
        if row[1] == "Charlotte":
            row[2] = "The American"

            #print(row[2])
        full_conferences.append(row[2])
    if row[4] not in full_teams:
        full_teams.append(row[4])
        full_conferences.append(row[5])
    
    if row[2] not in conference_names and row[2] != "AAC":
        conference_names.append(row[2])
    if row[5] not in conference_names and row[5] != "AAC":
        conference_names.append(row[5])


conf_names = conference_names

print(conf_names)

#print(conf_names)
#print(full_teams[:20])
#print(full_conferences[:20])

#print(neutral_field)


# Construct data structures as above
teams_dict = {}
for conf_name in conference_names:
    teams_dict[conf_name] = []

for i in range(len(full_conferences)):
    teams_dict[full_conferences[i]].append(full_teams[i])


# Input data into sim_data (K, N, p0, p1)
K = len(full_teams)
N = len(p0)
num_conferences = len(conf_names)



# Create a list for neutral team data [] X

#
# What does neutral look like in the bradley-terry? Make an adjusted bradley-terry with neutral data
# Adjust RPI so that it can take in the neutral IDs






########

#Problem: We have a list of teams, we need a list of indexes that correspond to them, starting at 1
team_indexes_dict = {}
for i in range(K):
    team_indexes_dict[full_teams[i]] = i + 1

#print(team_indexes_dict)
#print(full_teams)
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

#print(full_conferences)
#print([len(teams_dict[g]) for g in full_conferences])

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
    #print(model_data["neutral"])
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
    individual_model = cmdstanpy.CmdStanModel(stan_file="neutralbtdm.stan")
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

    return bt_r, alpha_hat, conf_strengths

#Ok, now let's calculate RPI



from collections import defaultdict

def calculate_rpi(data):
    teams = set()
    matches_by_team = defaultdict(list)

    team_0 = data["player0"]
    team_1 = data["player1"]
    results = data["y"]

    # Build match record for each team
    for match in range(data["N"]):
        t1 = team_0[match]
        t2 = team_1[match]
        result = results[match]

        teams.update([t1, t2])

        # Result from t1's perspective: win = -1, tie = 0, loss = 1
        matches_by_team[t1].append((t2, result))
        matches_by_team[t2].append((t1, -result))  # flip perspective

    # WP: win percentage = total wins / total games
    wp = {}
    for team in teams:
        wins = 0
        games = 0
        for opp, result in matches_by_team[team]:
            games += 1
            if result == -1:
                wins += 1
            elif result == 0:
                wins += 1 / 3
            # result == 1 → loss, 0 wins
        wp[team] = wins / games if games > 0 else 0

    # OWP: average opponent WP with current match excluded
    owp = {}
    for team in teams:
        owp_sum = 0
        count = 0
        for opp, result in matches_by_team[team]:
            opp_matches = matches_by_team[opp]

            # Recalculate opponent WP excluding the match vs `team`
            opp_wins = 0
            opp_games = 0
            for o_opp, o_result in opp_matches:
                if o_opp == team:
                    continue
                opp_games += 1
                if o_result == -1:
                    opp_wins += 1
                elif o_result == 0:
                    opp_wins += 0.5
            if opp_games > 0:
                owp_sum += opp_wins / opp_games
                count += 1
        owp[team] = owp_sum / count if count > 0 else 0

    # OOWP: average of opponents' OWPs
    oowp = {}
    for team in teams:
        oowp_sum = 0
        count = 0
        for opp, _ in matches_by_team[team]:
            oowp_sum += owp[opp]
            count += 1
        oowp[team] = oowp_sum / count if count > 0 else 0

    # Final RPI formula
    rpi = {
        team: [
            0.25 * wp[team] + 0.50 * owp[team] + 0.25 * oowp[team],
            wp[team],
            owp[team],
            oowp[team]
        ]
        for team in teams
    }

    return rpi




from collections import defaultdict

def calculate_better_rpi(data, triple):
    teams = set()
    matches_by_team = defaultdict(list)

    team_0 = data["player0"]
    team_1 = data["player1"]
    results = data["y"]

    # Build match record for each team
    for match in range(data["N"]):
        t1 = team_0[match]
        t2 = team_1[match]
        result = results[match]

        teams.update([t1, t2])

        # Result from t1's perspective: win = -1, tie = 0, loss = 1
        matches_by_team[t1].append((t2, result))
        matches_by_team[t2].append((t1, -result))  # flip perspective

    # WP: win percentage = total wins / total games
    wp = {}
    for team in teams:
        wins = 0
        games = 0
        for opp, result in matches_by_team[team]:
            games += 1
            if result == -1:
                wins += 1
            elif result == 0:
                wins += 1 / 3
            # result == 1 → loss, 0 wins
        wp[team] = wins / games if games > 0 else 0

    # OWP: average opponent WP with current match excluded
    owp = {}
    for team in teams:
        owp_sum = 0
        count = 0
        for opp, result in matches_by_team[team]:
            opp_matches = matches_by_team[opp]

            # Recalculate opponent WP excluding the match vs `team`
            opp_wins = 0
            opp_games = 0
            for o_opp, o_result in opp_matches:
                if o_opp == team:
                    continue
                opp_games += 1
                if o_result == -1:
                    opp_wins += 1
                elif o_result == 0:
                    opp_wins += 0.5
            if opp_games > 0:
                owp_sum += opp_wins / opp_games
                count += 1
        owp[team] = owp_sum / count if count > 0 else 0

    # OOWP: average of opponents' OWPs
    oowp = {}
    for team in teams:
        oowp_sum = 0
        count = 0
        for opp, _ in matches_by_team[team]:
            oowp_sum += owp[opp]
            count += 1
        oowp[team] = oowp_sum / count if count > 0 else 0

    # Final RPI formula
    rpi = {
        team: [
            triple[0] * wp[team] + triple[1] * owp[team] + triple[2] * oowp[team],
            wp[team],
            owp[team],
            oowp[team]
        ]
        for team in teams
    }

    return rpi
    






import copy
def adjusted_rpi(data, rpis, rpi_ranks, neutrals):
    adjusted_rpis = copy.deepcopy(rpis)
    neutral_ = data["neutral"]

    team_0 = data["player0"]
    team_1 = data["player1"]
    results = data["y"]
    bonus = [0] * data["K"]
    #for each match in data
    for index in range(data["N"]):
        t0 = team_0[index] - 1
        t1 = team_1[index] - 1

        t0_rpi = np.where(rpi_ranks == t0 + 1)[0][0]
        t1_rpi = np.where(rpi_ranks == t1 + 1)[0][0]

        is_neutral = bool(neutral_[index])


        if 1 == 1: #true
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
    #print("Bonus")
    #print(bonus)
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
num_simulations = 1


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


triples_er_ = [0] * len_triples
triples_r_s = [0] * len_triples
triples_rank_error = [0] * len_triples
triples_spearmans = [0] * len_triples
triples_confusion = [0] * len_triples

for trip in range(len_triples):
    triples_er_[trip] = [0] * num_simulations
    triples_r_s[trip] = [0] * num_simulations
    triples_spearmans[trip] = [0] * num_simulations
    triples_confusion[trip] = [0] * num_simulations


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
    # 
    """ 

    ########### END GENERATE GAME RESULTS ########### 



    ylist = y_l



    ########### SIMULATION DATA ########### 
    sim_data = {
        "K": K,
        "N": N,
        "player0": p0, 
        "player1": p1,
        "y": ylist,
        "neutral": neutral_field
    }

    """
    ### Calculate RPI ###
    ### Simple Model (no home advantage)
    #bt_r_s[sim], alpha_hat = calculate_btdm_simple_rank(sim_data)

    ### Advanced model (With home advantage)
    bt_r_s[sim], alpha_hat, conf_strengths = calculate_btdm_rank(sim_data)

    a_r_ = bt_r_s[sim]

    conf_strengths = {}
    ##Get conference strengths ##
    ## SIM 2+ ##
    for n in conf_names:
        conf_strengths[n] = 0

    for i in range(K):
        conf_strengths[full_conferences[i]] = conf_strengths[full_conferences[i]] + alpha_hat[i]

    for g in conf_names:
        #EDIT to work with the new conferences of different lengths
        #conf_strengths[g] = round(conf_strengths[g] / teams_per_conference, 4)
        conf_strengths[g] = round(conf_strengths[g] / len(teams_dict[g]), 4)

    bt_er_[sim] = list(atdr(a_r_, bt_r_s[sim], full_conferences).values())
    bt_spearmans[sim] = spearman(a_r_, bt_r_s[sim], full_conferences)
    ### End Calculate RPI ###
    """

    for trip in range(len_triples):
        #triples_er_ = [0] * len_triples
        #triples_r_s = [0] * len_triples
        #triples_rank_error = [0] * len_triples
        #triples_spearmans = [0] * len_triples
        #triples_confusion = [0] * len_triples  
        ### Calculate RPI ###

        rpi_full_values = calculate_better_rpi(sim_data, modified_rpi_triples[trip])
        rpi_values = [value[0] for value in rpi_full_values.values()]
        #turn into a numpy array for sorting function
        rpi_values_np = np.array(rpi_values)
        triples_r_s[trip][sim] = np.flip(np.argsort(rpi_values_np))
        triples_r_s[trip][sim] = triples_r_s[trip][sim] + 1

        ### Adjusted RPI (if needed) ###
        """
        adjusted_rpi_values = adjusted_rpi(sim_data, rpi_values, triples_r_s[trip][sim], [])
        rpi_values_np = np.array(adjusted_rpi_values)
        triples_r_s[trip][sim] = np.flip(np.argsort(rpi_values_np))
        triples_r_s[trip][sim] = triples_r_s[trip][sim] + 1
        #"""

        triples_er_[trip][sim] = list(atdr(a_r_, triples_r_s[trip][sim], full_conferences).values())
        triples_spearmans[trip][sim] = spearman(a_r_, triples_r_s[trip][sim], full_conferences)
        triples_confusion[trip][sim] = confusion_matrix(triples_r_s[trip][sim], sim_data)

    #################################




########### END RUN SIMULATIONS ########### 




########### PRINT SIMULATIONS OUTPUT ########### 


#list_atrd = [(full_teams[elem - 1] + ": " + str(alpha_hat[elem - 1])) for elem in a_r_]

list_rpi_comparison = [""] * K

"""
ind = 0
for elem in triples_r_s[0][0]:
    list_rpi_comparison.append(full_teams[elem - 1] + "(" + full_conferences[elem - 1] + "), ")
    ind = ind + 1
"""

sel = ["Clemson", "Duke", "NC State", "North Carolina", "SMU", "Pittsburgh", "Stanford", "Virginia", "Fordham", "Massachusetts", "Saint Louis", "Akron", "Providence", "Indiana", "Maryland", "Michigan", "UCLA", "Washington", "UC Santa Barbara", "Cornell", "Penn", "Missouri St.", "Western Mich.", "Denver", "Marshall", "Oregon St."]
aq = ["Ohio St.", "Georgetown", "Hofstra", "Dayton", "Wake Forest", "West Virginia", "Princeton", "Vermont", "San Diego", "Kansas City", "Charlotte", "Evansville", "Gardner-Webb", "Seattle U", "UC Davis", "SIUE", "Furman"]

ind = 0
for elem in triples_r_s[1][0]:
    #list_rpi_comparison[ind] = list_rpi_comparison[ind] + (full_teams[elem - 1] + "(" + full_conferences[elem - 1] + "), " + str(np.where(triples_r_s[0][0] == elem)[0][0] - ind))
    extra_str = "',"
    if full_teams[elem - 1] in sel:
        extra_str = " (S)',"
    elif full_teams[elem - 1] in aq:
        extra_str = " (AQ)',"
    list_rpi_comparison[ind] = ("'" + full_teams[elem - 1] + extra_str + "'(" + full_conferences[elem - 1] + ")', " + str(np.where(triples_r_s[0][0] == elem)[0][0] - ind))
    ind = ind + 1
    
print(list_rpi_comparison)
for i in range(K):
    print("[" + str(i) + "," + list_rpi_comparison[i] + "]")

    

