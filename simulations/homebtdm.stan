/**
 * Bradley-Terry DAVIDSON Model
 * 
 */
data {
  int<lower=0> K; // players
  int<lower=0> N; // games
  array[N] int<lower=1, upper=K> player1; // player 1 for game n
  array[N] int<lower=1, upper=K> player0; // player 0 for game n
  array[N] int<lower=-1, upper=1> y; // winner for game n
  //^ adjust to allow -1
}
parameters {
  vector[K] alpha; // ability for player n
  real gamma;
  real rho;
}
model {
  alpha ~ normal(0, 1); //This implicitly centers around 0
  // This allows for bayesian inference
  gamma ~ normal(0, 1);
  rho ~ normal(0, 1);

  //Now, we have 3 outcomes instead of two, so we have to use a target function
  for (n in 1:N) {
    //Note: Player1 is always at home
    real param_home = exp(alpha[player1[n]] + rho); //numerator for home win
    real param_away = exp(alpha[player0[n]]); //numerator for away win
    real param_tie = exp(gamma) * sqrt(param_home * param_away); //numerator for tie

    real denom = param_home + param_away + param_tie;
    if (y[n] == 1){ //Team 1 win (home)
      target += log(param_home / denom);
    } else if (y[n] == -1){ //Team 0 win (away)
      target += log(param_away / denom);
    } else { //tie
      target += log(param_tie / denom);
    }
  }

  //So we can't use this
  //y ~ bernoulli_logit(alpha[player1] - alpha[player0]);
}
generated quantities {
  //array[K] int<lower=1, upper=K> ranked = sort_indices_desc(alpha);
  
  array[K] int<lower=1, upper=K> ranking; // rank of player ability
  {
    array[K] int ranked_index = sort_indices_desc(alpha);
    for (k in 1 : K) {
      int m = ranked_index[k];
      ranking[m] = k;
    }
  }
}