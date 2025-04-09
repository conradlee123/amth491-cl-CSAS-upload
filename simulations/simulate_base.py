import cmdstanpy

#From https://www.rpubs.com/dkarwosk12345/560307

#NOTE: indexing of arrays starts at 1

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

def inv_logit(u):
    return 1 / (1 + np.exp(-u))

def center(u):
    return u - np.mean(u)

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



#Now Bradley-Terry BAYESIAN


individual_model = cmdstanpy.CmdStanModel(stan_file="homebtdm.stan")
#The difference is that this generates a distribution, rather than just a 
individual_posterior = individual_model.sample(data=mle_model_data)


# Compute posterior mean of alpha
alpha_samples = individual_posterior.stan_variable("alpha")
alpha_hat = np.mean(alpha_samples, axis=0)

plt.figure(figsize=(8, 6))
sns.scatterplot(x=alpha, y=alpha_hat, s=50)
plt.plot(alpha, alpha, color='green', linewidth=2)  # Green reference line
plt.xlabel("True Alpha")
plt.ylabel("Estimated Alpha Bayesian")
plt.title("Bayesian Fit Plot")
plt.show()

bt_r_ = individual_posterior.stan_variable(f'ranking')
#how should I interpret these?
#With this definition, ranking[k] holds the rank of player k
#(rather than the index of the player at rank k as before).

bt_r_ = np.mean(bt_r_, axis=0)
bt_r_ = np.argsort(bt_r_)
bt_r_ = bt_r_ + 1
#bt_r_.rank(method='first', ascending=True)
#print(bt_r_)







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

rpi_full_values = calculate_rpi(mle_model_data)
rpi_values = [value[0] for value in rpi_full_values.values()]
#turn into a numpy array for sorting function
rpi_values_np = np.array(rpi_values)
rpi_r_ = np.flip(np.argsort(rpi_values_np))
rpi_r_ = rpi_r_ + 1
#adjust for the bonus
adjusted_rpi_values = adjusted_rpi(mle_model_data, rpi_values, rpi_r_, [])
rpi_values_np = np.array(adjusted_rpi_values)
rpi_r_ = np.flip(np.argsort(rpi_values_np))
rpi_r_ = rpi_r_ + 1


#Now let's compare to true alpha
a_r_ = np.flip(np.argsort(alpha)) #flip() so that alphas are descending
a_r_ = a_r_ + 1

for index in range(K):
    print("Rank " + str(index + 1) + ": True Rank: Player #" + str(round(a_r_[index])) + ", alpha=" + str(round(alpha[a_r_[index] - 1], 3)) + "    BTDM: Player #" + str(round(bt_r_[index]))  + ", alpha=" + str(round(alpha_hat[bt_r_[index] - 1], 3)) + "    RPI: Player #" + str(round(rpi_r_[index]))  +  ", rpi=" + str(round(rpi_values_np[rpi_r_[index] - 1], 3)))



#Group-wise mean rank error
def atdr (truth, metric, conf):
    size = len(conf) # = K
    truth_pos = [0] * size
    metric_pos = [0] * size

    conf_score = {}
    conf_teams = {}
    for index in range(size):
        #print("")
        truth_pos[truth[index] - 1] = index + 1
        metric_pos[metric[index] - 1] = index + 1

    for index in range(size):
        diff = metric_pos[index] - truth_pos[index]
        if conf[index] in conf_score:
            conf_score[conf[index]] = conf_score[conf[index]] + diff
            conf_teams[conf[index]] = conf_teams[conf[index]] + 1
        else:
            conf_score[conf[index]] = diff
            conf_teams[conf[index]] = 1

    for key in conf_score:
        conf_score[key] = conf_score[key] / conf_teams[key]

    return conf_score

print(atdr(a_r_, bt_r_, conferences))
print(atdr(a_r_, rpi_r_, conferences))



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


print(spearman(a_r_, bt_r_, conferences))
print(spearman(a_r_, rpi_r_, conferences))



    


    
