import matplotlib.pyplot as plt
import numpy as np
import random
import cv2
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator


def generate_floorplan_contour(image, region, students):
    # Define a custom colormap with colors corresponding to student counts
    # Adjust the color_list to your preferred colors
    color_list = ['#00FFFF', '#00FF00', '#7FFF00', '#FFFF00', '#FFA500', '#FF6347', '#FF4500', '#FF0000']

  # Example colors
    cmap = LinearSegmentedColormap.from_list('custom_cmap', color_list, N=len(color_list))
    x_range = np.arange(image.shape[1])
    y_range = np.arange(image.shape[0])
    xx, yy = np.meshgrid(x_range, y_range)
    
    # Create an array for contour data
    contour_data = np.zeros_like(xx, dtype=np.float32)
    
    for seat_type, coordinates_list in region.items():
        for x1, x2, y1, y2 in coordinates_list:
            student_count = students.get(seat_type, 0)
            # Update the corresponding region in the contour data
            contour_data[y1:y2 + 1, x1:x2 + 1] = student_count
    
    # Apply Gaussian blur to the contour data
    contour_data = cv2.blur(contour_data, (80, 80), cv2.BORDER_DEFAULT)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(image)

    # Create the contour plot using the custom colormap
    contours = ax.contourf(xx, yy, contour_data, cmap=cmap, levels=len(color_list), alpha=0.8)

    # Create a color bar
    cbar = plt.colorbar(contours, ax=ax, orientation='horizontal')
    cbar.set_label('Student Count')

    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title('Level 3')
    plt.savefig('Level3_final.png')
    plt.show()


'''
generate_floorplan_contour(image_path, region, student_occupacy)
'''