import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide the main Tkinter window
Tk().withdraw()

# Prompt user to select a CSV file
file_path = askopenfilename(title="Select a CSV file", filetypes=[("CSV files", "*.csv")])
if not file_path:
    raise ValueError("No file selected.")

# Specify the columns to read from the CSV file
columns_to_read = ['Avg R', 'Avg G', 'Avg B']  # Update with your column names
df = pd.read_csv(file_path, usecols=columns_to_read)

# Define colors for each column
colors = ['red', 'green', 'blue']

# Create subplots
fig, axs = plt.subplots(2, 3, figsize=(15, 10))

# Get y-axis limits from the first column of original data
y_limits = (df.min().min(), df.max().max())

for i, column in enumerate(columns_to_read):
    # Original data
    axs[0, i].plot(df[column], label='Original', color=colors[i])
    axs[0, i].set_title(f'Original {column}')
    axs[0, i].set_ylim(y_limits)  # Set y-axis limits
    axs[0, i].legend()
    axs[0, i].grid(True)  # Show grid

    # LOESS smoothing
    smoothed_data = lowess(df[column], np.arange(len(df[column])), frac=0.3)  # Adjust frac for smoothing level
    axs[1, i].plot(smoothed_data[:, 0], smoothed_data[:, 1], label='LOESS Smoothed', color=colors[i])
    axs[1, i].set_title(f'LOESS Smoothed {column}')
    axs[1, i].set_ylim(y_limits)  # Set y-axis limits
    axs[1, i].legend()
    axs[1, i].grid(True)  # Show grid

plt.tight_layout()
plt.show()