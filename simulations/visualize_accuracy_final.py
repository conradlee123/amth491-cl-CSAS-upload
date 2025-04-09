import numpy as np
import matplotlib.pyplot as plt
pairings = [([0.9746218434343432, 0.981659722222222, 0.9734128787878785], [0.9577020202020204, 0.9564393939393941, 0.9501262626262628]), 
            ([0.7895672016143653, 0.7802506486270459, 0.7830176637736106], [0.7815041273998491, 0.7725981271719327, 0.7755343500042032]), 
            ([0.8005207273325248, 0.8216653683055362, 0.8071494996951817] , [0.7957908569650671, 0.8155636244588615, 0.801997277509959]), 
            ([0.7704713301779884, 0.7857357073113377, 0.7540668801771967] , [0.7658731421934122, 0.7814434948730627, 0.7494010113905754]), 
            ([0.7924385010207113, 0.7886342638973178, 0.7766145328633061] , [0.7884372683614242, 0.7852821167123457, 0.772453839563906]), 
            ([0.7653848219779715, 0.7547586620724211, 0.7599386875477638] , [0.7602672444070864, 0.7503263895663028, 0.7548607378118142]), 
            ([0.7905170193514429, 0.7642035274926181, 0.7842703603010484] , [0.7849060484736551, 0.7612653023719982, 0.7824599267607414])]

pairings_mean = [(np.mean(elem[0]), np.mean(elem[1])) for elem in pairings]

print(pairings_mean)

# Unzip the data into two lists
left_values, right_values = zip(*pairings_mean)

# Create an array for the indices
indices = np.arange(len(pairings_mean))

# Define the width of the bars
bar_width = 0.35

# Create the plot
fig, ax = plt.subplots()

# Plot the bars for the left and right values
ax.bar(indices - bar_width / 2, left_values, bar_width, label='Bradley-Terry')
ax.bar(indices + bar_width / 2, right_values, bar_width, label='RPI')

# Labeling
ax.set_xlabel('Simulation Number')
ax.set_ylabel('Accuracy Rate')
ax.set_title('Prediction Accuracy for Bradley-Terry vs. RPI Rankings')
ax.set_xticks(indices)
ax.set_xticklabels([f'Sim {i+11}' for i in indices])
ax.legend()

ax.set_ylim(0.7, 1)


# Show the plot
plt.show()