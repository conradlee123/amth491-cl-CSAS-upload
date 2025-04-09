import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Given data
conf_strengths_1 = [0.4151, 1.0708, 0.7968, -1.4018, 0.5796, -1.1275, -0.7731, 0.4006, -1.2677, -0.4228, -0.8663, -2.0063, -0.7617, -0.2295, 0.2494, 0.1536, 0.2483, 0.1132, 0.8471, -0.5949, 2.0992, 0.0675, 1.2579]
btdm_rank_errors_1 = [4.6845, 16.4492, 10.3227, -21.8396, 7.1629, -9.0026, -12.0109, 4.853, -25.3462, -7.5537, -11.7354, -16.9088, -10.6034, -9.9078, 2.1229, -6.0115, 1.0592, 8.4953, 19.9795, 3.6431, 22.0332, -3.071, 15.8784]
rpi_rank_errors_1 = [2.2144, 3.3968, 5.8489, -4.502, 6.6138, -1.4938, -12.4367, 13.6894, -12.1744, -15.5094, -8.1314, -7.6368, -7.424, -10.1733, -5.1306, 4.5718, 4.6201, 10.7731, 1.4822, 12.2139, 12.093, 0.801, 3.6008]

# Compute differences between RPI and BTD rank errors
rank_error_differences = np.array(rpi_rank_errors_1) - np.array(btdm_rank_errors_1)

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
plot_scatter_updated(conf_strengths_1, btdm_rank_errors_1, 
                     "Conference Strength vs. BTDM Rank Errors (Round 1)", 
                     "Conference Strength", "BTDM Rank Errors")

plot_scatter_updated(conf_strengths_1, rpi_rank_errors_1, 
                     "Conference Strength vs. RPI Rank Errors (Round 1)", 
                     "Conference Strength", "RPI Rank Errors")

plot_scatter_updated(conf_strengths_1, rank_error_differences, 
                     "Conference Strength vs. (RPI - BTDM Rank Errors) (Round 1)", 
                     "Conference Strength", "(RPI - BTDM Rank Errors)")


conf_strengths_2 = [0.1669, -0.7172, -0.0937, 0.3688, 0.2234, 0.1517, -1.3867, -0.156, -0.6146, 0.1879, 0.2943, 0.7924, 1.0999, -0.9632, 0.8856, -0.1087, -0.7396, 2.1413, 0.805, -0.4158, -0.6725, -0.7032, -0.2017]
btdm_rank_errors_2 = [-0.7496, -12.7805, 1.9812, 1.6977, 4.3835, 3.6762, -19.247, -2.6298, -21.4334, 6.1263, 11.4302, 10.3185, 22.6272, -18.151, 17.9076, 0.8761, -20.9676, 22.1272, 15.5792, 1.1279, -3.8019, 5.422, -3.4132]
rpi_rank_errors_2 = [-3.7556, -15.1321, 4.3351, 10.2708, 1.3615, 0.1206, -14.9643, 2.6505, -14.383, -5.0899, 13.0628, 11.0163, 12.3754, -13.5836, 11.5617, 12.1476, -6.9029, 10.0063, -3.3501, 13.7683, 2.0762, -2.196, -4.5012]

# Compute differences between RPI and BTD rank errors
rank_error_differences2 = np.array(rpi_rank_errors_2) - np.array(btdm_rank_errors_2)

plot_scatter_updated(conf_strengths_2, btdm_rank_errors_2, 
                     "Conference Strength vs. BTDM Rank Errors (Round 2)", 
                     "Conference Strength", "BTDM Rank Errors")

plot_scatter_updated(conf_strengths_2, rpi_rank_errors_2, 
                     "Conference Strength vs. RPI Rank Errors (Round 2)", 
                     "Conference Strength", "RPI Rank Errors")

plot_scatter_updated(conf_strengths_2, rank_error_differences2, 
                     "Conference Strength vs. (RPI - BTDM Rank Errors) (Round 2)", 
                     "Conference Strength", "(RPI - BTDM Rank Errors)")






conf_strengths_3 = [-1.2969, -0.1929, 0.5177, -0.3946, -0.6891, 0.3582, 0.1772, -0.2793, -0.0141, 0.0033, -0.4207, 1.0169, -0.5795, 1.1011, 0.0499, -0.1961, 2.6736, -2.073, 0.6336, 1.1086, -0.5565, -1.4251, 0.3446]
btdm_rank_errors_3 = [-19.3976, -2.696, 4.6478, -7.676, -15.2753, 1.5016, 4.9445, -9.1753, 7.8297, 0.8065, -3.6292, 8.7902, -3.8274, 27.5136, -1.437, 5.8325, 29.9988, -18.5867, 10.584, 6.5444, -11.6029, -12.277, 2.3368]
rpi_rank_errors_3 = [-9.1549, -13.0465, 2.0343, 2.8628, -11.4538, -1.0939, 0.433, 1.0472, 17.0526, -11.3297, 7.3742, 11.5038, 2.9744, 19.5264, -0.0519, 16.1171, 23.1626, -10.5216, -7.2655, 0.0856, -10.2521, -24.536, -2.1282]

# Compute differences between RPI and BTD rank errors
rank_error_differences3 = np.array(rpi_rank_errors_3) - np.array(btdm_rank_errors_3)

plot_scatter_updated(conf_strengths_3, btdm_rank_errors_3, 
                     "Conference Strength vs. BTDM Rank Errors (Round 3)", 
                     "Conference Strength", "BTDM Rank Errors")

plot_scatter_updated(conf_strengths_3, rpi_rank_errors_3, 
                     "Conference Strength vs. RPI Rank Errors (Round 3)", 
                     "Conference Strength", "RPI Rank Errors")

plot_scatter_updated(conf_strengths_3, rank_error_differences3, 
                     "Conference Strength vs. (RPI - BTDM Rank Errors) (Round 3)", 
                     "Conference Strength", "(RPI - BTDM Rank Errors)")