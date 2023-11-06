import cv2
import numpy as np
import matplotlib.pyplot as plt
import io

def generate_heatmap(region, image_path, student_occupancy):
    # Load your floor plan image
    image = cv2.imread(image_path)

    def map_students_to_color(student_count):
        # Use a continuous colormap from blue to red
        # The colormap range is [0, 1]
        normalized_count = student_count / 100  # Adjust as needed
        # Create a colormap ranging from blue (0, 0, 255) to red (255, 0, 0)
        color = (1 - normalized_count, 0, normalized_count)
        return (np.array(color) * 255).astype(int)

    heatmap = np.zeros_like(image, dtype=np.uint8)

    for seat_type, coordinates_list in region.items():
        student_count = student_occupancy.get(seat_type, 0)
        color = map_students_to_color(student_count)
        for x1, x2, y1, y2 in coordinates_list:
            heatmap[y1:y2 + 1, x1:x2 + 1] = color

    # Overlay the heatmap on the floor plan
    overlay = cv2.addWeighted(image, 1.0, heatmap, 0.7, 0)

    plt.imshow(overlay)
    plt.title('Floor Plan with Student Count Heatmap Overlay')
    plt.show()

# Example usage:
'''
region_coordinates = {'Windowed.Seats':[[36 ,1220,40,132],[40, 128,136,1308],[144,1224,1212,1304],[1644,4532,780,900],[1912,2668,2396,2528],[44,1912,2840,2960],[4720,5548,784,904],[5548,5688,784,2948],[4720,5548,2836,2948]],
                             'X4.man.tables':[[288,1068,196,316],[1304,1568,368,736],[212,1004,2140,2260],[2156,2425,2134,2255],[1432,1704,2144,2264],[4108,4372,1045,1985]],
                             'X8.man.tables':[[1992,3904,1024,1188],[1300,1828,2528,2700]]}
student_occupancy = {'Windowed.Seats':30, 'X4.man.tables':20,'X8.man.tables':80}

image_path = '/Users/yg/Downloads/dsa3101-2310-04-library/L5_grayscale_image.jpg'

generate_heatmap(region, image_path, student_occupancy)
'''

def generate_floorplan_contour(image_path, region, student_occupancy):
    image = cv2.imread(image_path)
    x_range = np.arange(image.shape[1])
    y_range = np.arange(image.shape[0])
    xx, yy = np.meshgrid(x_range, y_range)
    
    # Create an array for contour data
    contour_data = np.zeros_like(xx, dtype=np.float32)
    
    for seat_type, coordinates_list in region.items():
        for x1, x2, y1, y2 in coordinates_list:
            student_count = student_occupancy.get(seat_type, 0)
            # Update the corresponding region in the contour data
            contour_data[y1:y2 + 1, x1:x2 + 1] = student_count


    # Apply Gaussian blur to the contour data
    contour_data = cv2.GaussianBlur(contour_data, ksize=(251, 251), sigmaX=25, sigmaY=25)

    # Apply the mask to make regions with 0 students transparent
    #contour_data *= mask

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(image)

    # Create the contour plot
    contours = ax.pcolormesh(xx, yy, contour_data, cmap="jet", alpha=0.9)

    ax.set_title('Contour Plot')
    plt.show()

'''
generate_floorplan_contour(image_path, region, student_occupacy)
'''