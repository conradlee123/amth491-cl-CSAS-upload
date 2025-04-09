import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Given data
conf_strengths_1 = [0.1691, 0.2988, 0.2227, -0.5591, -0.4551, 0.1971, 0.1945, -0.6461, -0.1795,
 0.7334, -0.4941, 0.0494, 0.4794, 0.2259, 0.0809, -0.4243, -0.6094, -0.32,
 0.539, 0.055, 0.0743, 0.0064]

btdm_rank_errors_1 = [0] * 22
rpi_rank_errors_1 = [-7.7143, -10.9, -5.6364, 20.6667, 11.0, -5.625, -8.1667, 16.4615, 8.4, -16.6667, 16.25, 10.8333, -10.2, -5.6667, -10.125, 14.5, 19.875, 2.9, -20.0909, 7.2, -2.5556, -8.25]

# 0.25 0.3 0.45
triple_re_1 = [-4.7143, -11.4, -4.3636, 16.8889, 6.3, 0.375, -7.8333, 10.0, 6.1, -11.0, 10.75, 14.0, -4.8, -2.1111, -5.0, 10.0, 15.125, 2.0, -18.1818, 7.8, -4.2222, -8.75]
# (0.3, 0.25, 0.45)
triple_re_2 = [-2.4286, -8.3, -3.0, 11.5556, 4.6, 0.75, -6.1667, 4.7692, 2.9, -7.1333, 8.25, 10.8333, -2.8, -1.0, -1.125, 6.875, 8.5, 1.4, -12.5455, 7.0, -2.6667, -7.5]
#(0.3, 0.3, 0.4)
triple_re_3 = [-4.5714, -8.5, -3.5455, 12.6667, 4.6, -0.75, -5.3333, 5.6923, 3.8, -7.9333, 9.0, 11.1667, -2.6, -1.7778, -0.75, 7.25, 9.625, 1.5, -13.3636, 7.9, -2.3333, -7.5]
# (0.35, 0.35, 0.3)
triple_re_4 = [-2.8571, -6.5, -1.6364, 8.6667, 3.5, -1.875, -3.5, 1.6923, -0.4, -6.0, 8.0, 9.6667, -2.4, -1.4444, 1.25, 5.625, 6.5, 0.3, -7.7273, 8.3, -0.8889, -7.25]
# (0.4, 0.35, 0.25)
triple_re_5 = [-0.8571, -4.7, -1.0, 5.1111, 2.7, -2.125, -2.9167, -1.0769, -1.7, -4.2, 5.875, 8.8333, -0.6, -1.2222, 2.5, 3.875, 1.625, -0.4, -3.1818, 8.5, 0.0, -6.625]
# (0.45, 0.4, 0.15)
triple_re_6 = [0.0714, -3.9, 0.1818, 2.1111, 0.6, -2.5, -2.0, -2.9231, -2.6, -3.1333, 4.875, 8.3333, -0.4, -1.0, 3.875, 3.5, -0.375, -0.3, -0.7273, 8.7, 1.2222, -6.875]

#(0.15, 0.3, 0.55)
triple_re_best = [-8.3571, -17.9, -7.4545, 31.1111, 9.2, 2.75, -13.5, 20.3077, 15.2, -19.7333, 14.75, 18.0, -13.2, -1.7778, -11.0, 17.875, 30.0, 1.6, -29.4545, 7.7, -10.5556, -10.875]



# Updated function with requested modifications
def plot_scatter_updated(x, y, title, xlabel, ylabel):
    # Compute linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Generate regression line
    reg_line = np.array(x) * slope + intercept

    # Create scatter plot
    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, color='blue', marker='x', label=f'r={r_value:.2f}, p={p_value:.4f}')
    plt.plot(x, reg_line, color='red', linewidth=2, label='Best Fit Line')  # Solid, narrower line
    
    # Labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

# Generate the updated scatter plots
#plot_scatter_updated(conf_strengths_1, triple_re_1, 
#                    "Conference Strength vs. Triple Rank Errors (Round 1)", 
#                   "Conference Strength", "Triple Rank Errors")

#plot_scatter_updated(conf_strengths_1, [- elem for elem in rpi_rank_errors_1], 
                     #"Conf. Strength vs. Inverted RPI Rank Error, 2024 Season", 
                     #"Conference Strength", "RPI Rank Error (Inverted)")



# Compute differences between RPI and BTD rank errors
#rank_error_differences =  np.array(triple_re_best) - np.array(btdm_rank_errors_1)

#plot_scatter_updated(conf_strengths_1, [- elem for elem in triple_re_best], 
                     #"Conf. Strength vs. Best RPI Weights\nRank Error (Inverted), 2024 Season", 
                     #"Conference Strength", "(0.15, 0.3, 0.55) Rank Error (Inverted)")

"""
# Compute differences between RPI and BTD rank errors
rank_error_differences =  np.array(triple_re_2) - np.array(rpi_rank_errors_1)

plot_scatter_updated(conf_strengths_1, rank_error_differences, 
                     "Conf. Strength vs. Rank Error Diff. (Best Weighting - RPI)", 
                     "Conference Strength", "(0.15, 0.3, 0.55) - RPI Rank Error")

# Compute differences between RPI and BTD rank errors
rank_error_differences =  np.array(triple_re_3) - np.array(rpi_rank_errors_1)

plot_scatter_updated(conf_strengths_1, rank_error_differences, 
                     "Conf. Strength vs. Rank Error Diff. (Best Weighting - RPI)", 
                     "Conference Strength", "(0.15, 0.3, 0.55) - RPI Rank Error")

# Compute differences between RPI and BTD rank errors
rank_error_differences =  np.array(triple_re_4) - np.array(rpi_rank_errors_1)

plot_scatter_updated(conf_strengths_1, rank_error_differences, 
                     "Conf. Strength vs. Rank Error Diff. (Best Weighting - RPI)", 
                     "Conference Strength", "(0.15, 0.3, 0.55) - RPI Rank Error")


# Compute differences between RPI and BTD rank errors
rank_error_differences =  np.array(triple_re_5) - np.array(rpi_rank_errors_1)

plot_scatter_updated(conf_strengths_1, rank_error_differences, 
                     "Conf. Strength vs. Rank Error Diff. (Best Weighting - RPI)", 
                     "Conference Strength", "(0.15, 0.3, 0.55) - RPI Rank Error")
"""


import matplotlib.pyplot as plt

# Data
corrs = [0.7483222222,	0.7324222222,	0.62725,	0.6633611111,	0.5594611111,	0.2851722222,	0.07216111111]
p_vals = [0.0, 0.0, 0.0, 0.0, 0.0004, 0.033, 0.3584, 0.0]

"""
test_rpi_triples = [(0.25, 0.3, 0.45), 
                        (0.3, 0.25, 0.45), 
                        (0.3, 0.3, 0.4),  
                        (0.35, 0.35, 0.3), 
                        (0.4, 0.35, 0.25),
                        (0.45, 0.4, 0.15)]
"""

triples_names = [(0.25, 0.3, 0.45),
                 (0.3, 0.25, 0.45),
                 (0.3, 0.3, 0.4),
                 (0.35, 0.35, 0.3),
                 (0.4, 0.35, 0.25),
                 (0.45, 0.4, 0.15)]

labels = ["Std. RPI"] + [str(i) for i in triples_names]

# Create bar colors
colors = ['green', 'skyblue', 'skyblue', 'skyblue', 'skyblue', 'skyblue', 'skyblue']

# Plot
plt.figure(figsize=(8, 5))
bars = plt.bar(labels, corrs, color=colors)

# Add p-values on top of bars
for i, (bar, p) in enumerate(zip(bars, corrs)):
    p_text = f"{p:.3f}"
    if p < 0.05:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, p_text,
                 ha='center', va='bottom', fontsize=10)
    else:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, p_text,
                 ha='center', va='bottom', fontsize=10)






plt.ylabel("Corr. between Conf. Strength and Rank Error")
plt.title("Avg. Simulation Correlation (R) Between Estimated Conf. Strength\nand Rank Error (Inverted), Std. RPI and Selected Weightings")
plt.ylim(0, max(corrs) + 0.1)
plt.tight_layout()
plt.show()





acc_labels = ["BTDM", "Std. RPI"] + [str(elem) for elem in triples_names]
print(acc_labels)
accuracy_values = [0.7790337222, 0.7746389444, 0.7791637222, 0.7792082222, 0.7793940556, 0.7792554444, 0.7789007778, 0.7786203333]

import numpy as np

# Sample data
#accuracy_values = np.random.uniform(0.6, 0.95, 7)  # Random accuracy values between 60% and 95%
labels = acc_labels
colors = ['orange', 'green'] + ['skyblue'] * 6

# Plot
plt.figure(figsize=(8, 5))
bars = plt.bar(labels, accuracy_values, color=colors)

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.0005, f"{height:.4f}",
             ha='center', va='bottom', fontsize=10)

plt.ylabel("Accuracy")
plt.title("Avg. Simulation Predictive Accuracy of Rankings for Bradley-Terry,\nStd. RPI and Selected Weightings")
plt.ylim(0.77, 0.783)
plt.tight_layout()
plt.show()



import matplotlib.pyplot as plt

data = [
    ['Simulation', 'Best RPI Weighting', 'Avg. Accuracy'],
    ['Synthetic Matchups, No Home\nAdvantage, Balanced Conferences', "(0.25, 0.3, 0.45)", 0.785428],
    ['Synthetic Matchups, No Home\nAdvantage, Imbalanced Conferences', "(0.25, 0.3, 0.45)", 0.808670],
    ['Synthetic Matchups, Home\nAdvantage, Balanced Conferences', "(0.45, 0.4, 0.15)", 0.767450],
    ['Synthetic Matchups, Home \nAdvantage, Imbalanced Conferences', "(0.3, 0.25, 0.45)", 0.791365],
    ['2024 Matchups, Home Advantage,\nBalanced Conferences', "(0.45, 0.4, 0.15)", 0.764676],
    ['2024 Matchups, Home Advantage,\nImbalanced Conferences', "(0.3, 0.3, 0.4)", 0.785131],
]

fig, ax = plt.subplots()
ax.axis('off')  # hide plot

table = ax.table(cellText=data, loc='center')
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1.2, 1.2)

# Adjust column widths: iterate over all cells
for (row, col), cell in table.get_celld().items():
    if col == 0:
        cell.set_width(0.35)  # Wider first column
    else:
        cell.set_width(0.2)  # Narrower others
    cell.set_height(0.1)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.tight_layout(pad=-5)

plt.show()