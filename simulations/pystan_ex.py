import stan
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

# observations
N = K**2
player1 = np.empty(N, dtype=int)
player0 = np.empty(N, dtype=int)

for n in range(N):
    #Note: adjust K down one and then move it back up
    players = np.random.choice(np.arange(K - 1), size=2, replace=False)
    player0[n] = players[0] + 1
    player1[n] = players[1] + 1


#NOTE: IMPORTANT
#do -1 to adjust down for the list we're pulling from
log_odds_player1 = alpha[player1 - 1] - alpha[player0 - 1]
prob_win_player1 = inv_logit(log_odds_player1)
print(prob_win_player1[0:10])
y = np.random.binomial(1, prob_win_player1)

df = pd.DataFrame({'player0': player0, 'player1': player1, 'y': y})
print(df.head(30))




stan_code = """
data {
  int<lower=0> K; // players
  int<lower=0> N; // games
  array[N] int<lower=1, upper=K> player1; // player 1 for game n
  array[N] int<lower=1, upper=K> player0; // player 0 for game n
  array[N] int<lower=0, upper=1> y; // winner for game n
}
parameters {
  vector[K - 1] alpha_raw; // ability for players 1:K-1
}
transformed parameters {
  // enforces sum(alpha) = 0 for identifiability
  vector[K] alpha = append_row(alpha_raw, -sum(alpha_raw));
}
model {
  y ~ bernoulli_logit(alpha[player1] - alpha[player0]);
}
"""

p0 = player0.tolist()
p1 = player1.tolist()
ylist = y.tolist()

print(len(p0))

# Prepare data for Stan model
mle_model_data = {
    "K": K,
    "N": N,
    "player0": p0, 
    "player1": p1,
    "y": ylist
}
#print(mle_model_data)



#posterior = stan.build(stan_code, data=mle_model_data, random_seed=1)


# Perform sampling
#fit = posterior.sample(num_samples=1000)

sm = cmdstanpy.CmdStanModel(stan_file="individual-uniform.stan")

#NO MLE OPTIMIZATION FOR PYSTAN3!!!!
#https://discourse.mc-stan.org/t/mle-and-optimize-in-pystan3/24023

# Perform optimization (MLE estimation)
mle_model_estimates = sm.optimize(data=mle_model_data, iter=1000, inits=0)

#print(mle_model_estimates.optimized_params_dict)

# estimated alpha values
a_ = mle_model_estimates.stan_variable(f'alpha')

#print(a_)
#print(alpha)

alpha_star = np.array([a_[i] for i in range(K)])

plt.figure(figsize=(8, 6))
sns.scatterplot(x=alpha, y=alpha_star, s=50)
plt.plot(alpha, alpha, color='green', linewidth=2)  # Green reference line
plt.xlabel("True Alpha")
plt.ylabel("Estimated Alpha")
plt.title("MLE Fit Plot")
plt.show()


r_ = mle_model_estimates.stan_variable(f'ranked')

#ranked_players = np.array([r_[i] for i in range(K)])
#print(np.round(ranked_players, decimals=0))

#true_r_ = sorted(alpha)

for index in range(K):
    print("Rank " + str(index + 1) + ": Player #" + str(round(r_[index])))




#Now Bradley-Terry

individual_model = cmdstanpy.CmdStanModel(stan_file="individual.stan")
individual_posterior = individual_model.sample(data=mle_model_data)


alpha_summary = individual_posterior.summary(percentiles=[5, 50, 95])
print(alpha_summary.loc[alpha_summary.index.str.startswith("alpha")])


# Compute posterior mean of alpha
alpha_samples = individual_posterior.stan_variable("alpha")
alpha_hat = np.mean(alpha_samples, axis=0)
print(alpha_hat)

plt.figure(figsize=(8, 6))
sns.scatterplot(x=alpha, y=alpha_hat, s=50)
plt.plot(alpha, alpha, color='green', linewidth=2)  # Green reference line
plt.xlabel("True Alpha")
plt.ylabel("Estimated Alpha")
plt.title("BT Fit Plot")
plt.show()

bt_r_ = mle_model_estimates.stan_variable(f'ranked')

for index in range(K):
    print("Rank " + str(index + 1) + ": BT: Player #" + str(round(bt_r_[index])) + "  MLE: Player #" + str(round(r_[index])))