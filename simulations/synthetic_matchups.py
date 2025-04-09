import copy
import random
teams_per_conference = 4
num_conferences = 22
conference_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V"]

def generate_teams(conf_names, teams_per):
    teams = []
    for conf_name in conf_names:
        for t in range(teams_per):
            teams.append(conf_name + str(t + 1))

    return teams

full_teams = generate_teams(conference_names, teams_per_conference)
full_conferences = [s[0] for s in full_teams]

#let's make a dict of all of the teams, arranged by conference
teams_dict = {}
for conf_name in conference_names:
    teams_dict[conf_name] = []

for i in range(len(full_conferences)):
    teams_dict[full_conferences[i]].append(full_teams[i])

def generate_conference_pairings(teams, two_legged):
    team0 = []
    team1 = []

    m = 0
    for key in teams:
        num_teams_conf = len(teams[key])
        for i in range(num_teams_conf - 1):
            for j in range(i + 1, num_teams_conf):
                if two_legged:
                    team0.append(teams[key][i])
                    team0.append(teams[key][j])
                    team1.append(teams[key][j])
                    team1.append(teams[key][i])
                else:
                    #don't do random 
                    #we'll alternate pairings deterministically
                    if m == 0: #i away
                        team0.append(teams[key][i])
                        team1.append(teams[key][j])
                        m = 1
                    else: #i home
                        team0.append(teams[key][j])
                        team1.append(teams[key][i])
                        m = 0

    return team0, team1





def generate_random_pairings(teams, num_pairings):
    teams_save = copy.deepcopy(teams)
    conf_names = list(teams.keys())
    #print(conf_names)

    team0 = []
    team1 = []
    #teams_save = teams

    #let's make a dict of all of the teams, 
    num_conf = len(conf_names)
    total_teams = num_conf * len(teams[conf_names[0]])

    for pair in range(num_pairings):
        paired = 0
        while paired < total_teams:
            for ci1 in range(round(num_conf / 2)):
                ci2 = random.randrange(len(conf_names) - 1)
                if ci2 >= 0:
                    ci2 = ci2 + 1

                c1 = conf_names[0] 
                c2 = conf_names[ci2]
                conf_names.remove(c1)
                conf_names.remove(c2)

                t1 = random.choice(teams_save[c1])
                teams_save[c1].remove(t1)

                t2 = random.choice(teams_save[c2])
                teams_save[c2].remove(t2)

                if random.randint(0, 1) == 0: #t1 away
                    team0.append(t1)
                    team1.append(t2)
                else: #t1 home
                    team0.append(t2)
                    team1.append(t1)

                paired = paired + 2
            
            conf_names = list(teams.keys())

        teams_save = copy.deepcopy(teams)

    return team0, team1

player0, player1 = generate_random_pairings(teams_dict, 8)

player_conf0, player_conf1 = generate_conference_pairings(teams_dict, False)

p0 = player0 + player_conf0
p1 = player1 + player_conf1

###
team_indexes_dict = {}
for i in range(len(full_teams)):
    team_indexes_dict[full_teams[i]] = i + 1

for i in range(len(p0)):
    p0[i] = team_indexes_dict[p0[i]]
    p1[i] = team_indexes_dict[p1[i]]
###

#print(p0)
#print(p1)

##### NOw testing with simulating matchups

import numpy as np
import cmdstanpy
def center(u):
    return u - np.mean(u)

K = teams_per_conference * num_conferences

alpha = center(np.random.normal(size=K))

#True alpha rankings
a_r_ = np.flip(np.argsort(alpha)) #flip() so that alphas are descending
a_r_ = a_r_ + 1

ylist = []
conf_strengths = {}

"""
for tm_index in range(len(p1)):
    index_diff = np.where(a_r_ == p0[tm_index])[0][0] - np.where(a_r_ == p1[tm_index])[0][0]
    ylist.append(round(index_diff / abs(index_diff)))

"""

for tm_index in range(len(p1)):
    ylist.append(random.randint(-1, 1))

##Get conference strengths ##
for n in conference_names:
    conf_strengths[n] = 0
        
"""
print(p0[:20])
print(p1[:20])
print(ylist[:20])
print(a_r_)
print(conf_strengths)
"""




"""

##Get conference strengths ##
for n in conference_names:
    conf_strengths[n] = 0

for i in range(K):
    conf_strengths[full_conferences[i]] = conf_strengths[full_conferences[i]] + (K - np.where(a_r_ == i + 1)[0][0])

for g in conference_names:
    conf_strengths[g] = round(conf_strengths[g] / teams_per_conference, 4)
##End get conference strengths ##

print(conf_strengths)"
"""




        
    


