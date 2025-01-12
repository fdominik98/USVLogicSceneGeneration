import os
from PIL import Image
import numpy as np

from utils.file_system_utils import ASSET_FOLDER

gradient_image_path = f'{ASSET_FOLDER}/images/gradient.png'
striped_image_path = f'{ASSET_FOLDER}/images/distr.png'

gradient_image = Image.open(gradient_image_path)
striped_image = Image.open(striped_image_path)

# Convert images to numpy arrays for processing
gradient_array = np.array(gradient_image)
striped_array = np.array(striped_image)

# Display shapes to understand dimensions
gradient_array.shape, striped_array.shape


# Average the colors along the width of the gradient image to create a 1D gradient mapping
# (57 rows, each row representing a color to a specific value from 0.0 to 0.8)
gradient_1d = np.mean(gradient_array[:, :, :3], axis=1)  # Take RGB channels and average across width

# Define the value range from 0.0 to 0.8, mapping each row in the gradient to a value
value_range = np.linspace(0.0, 0.8, len(gradient_1d))

# Flatten the striped image to get each pixel color for comparison
striped_pixels = striped_array[:, :, :3].reshape(-1, 3)

# Function to find the closest color in the gradient mapping
def map_color_to_value(color, gradient_1d, value_range):
    # Calculate Euclidean distance to each color in gradient_1d
    distances = np.linalg.norm(gradient_1d - color, axis=1)
    # Find the index of the closest color
    closest_index = np.argmin(distances)
    # Map to corresponding value
    return value_range[closest_index]

# Map each pixel in the striped image to a value based on the gradient
mapped_values = np.array([map_color_to_value(pixel, gradient_1d, value_range) for pixel in striped_pixels])

# Calculate mean and median of the mapped values
mean_value = np.mean(mapped_values)
median_value = np.median(mapped_values)

mean_value, median_value



import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 12

# Plot the distribution as a violin plot
fig, axi = plt.subplots(1,1,figsize=(2, 3))


# Create the violin plot
violinplot = axi.violinplot(mapped_values, showmeans=True, showmedians=True)

# Add labels and title
axi.set_title("4 Vessels")
axi.set_ylabel("Highest DS-based risk index")

for patch in violinplot['bodies']:
    patch.set_facecolor('brown')           # Set fill color
    patch.set_linewidth(1.5) 
    
violinplot['cmeans'].set_color('black')
violinplot['cmeans'].set_linewidth(2)
violinplot['cmedians'].set_color('grey')
violinplot['cmedians'].set_linewidth(2)
violinplot['cmedians'].set_linestyle(':')

axi.set_xticks([1], ['Base'])
axi.set_xticklabels(['Base'], rotation=0, ha='center', fontweight='bold')    

axi.text(1, 0.8 * 1.05, f'601', ha='center', va='center', fontsize=10, horizontalalignment='center')

axi.set_ylim(0, 1 * 1.15)

fig.tight_layout()

file_name = f'wang2024_risk'
image_folder = f'{ASSET_FOLDER}/images/exported_plots/wang'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)
fig.canvas.figure.savefig(f'{image_folder}/{file_name}.svg', format='svg', bbox_inches='tight', dpi=350)
fig.canvas.figure.savefig(f'{image_folder}/{file_name}.pdf', format='pdf', bbox_inches='tight', dpi=350)
print('image saved')

# Display the plot
plt.show()