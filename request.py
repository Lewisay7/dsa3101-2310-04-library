from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import plotly as pltly
import pandas as pd
import random
import cv2
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import numpy as np
from output1 import *
import io 

app = Flask(__name__, static_url_path='/', static_folder='templates')


# Load dataset
csv_file_path = 'datasets/model_output.csv'
df = pd.read_csv(csv_file_path)

#floorplan path
images_path = {'3': "floorplan_images/L_3.png",
               '4':"floorplan_images/L_4.jpg",
               '5': 'floorplan_images/L_5.jpg',
               '6':"floorplan_images/L_6.jpg",
               '6Chinese':"floorplan_images/L_6C.jpg"}

#grayscale floorplan images
greyscale_images = {'3': "floorplan_images/L3_grayscale_image.jpg",
               '4':"floorplan_images/L4_grayscale_image.jpg",
               '5': 'floorplan_images/L5_grayscale_image.jpg',
               '6':"floorplan_images/L6_grayscale_image.jpg",
               '6Chinese':"floorplan_images/L6C_grayscale_image.jpg"}

#seat type coordinates
region_coordinates = {'3':{'Discussion.Cubicles':[[4103,5450,522,748]],'Soft.seats':[[1738,811,187,330],[1969,3542,621,1215],[4356,5467,192,330],[4488,5456,2860,3014]],
                            'Moveable.seats':[[4367,5362,1050,2090]]},
                       '4':{'Soft.seats':[[1166,1639,682,1155],[2178,2656,1309,1721],[3228,3822,792,902],[4625,5098,1639,2530],[4537,5175,2799,2909]],
                             'Sofa':[[1039,1749,1375,1584], [2909, 3987,1364,1606]]},
                       '5':{'Windowed.Seats':[[36 ,1220,40,132],[40, 128,136,1308],[144,1224,1212,1304],[1644,4532,780,900],[1912,2668,2396,2528],[44,1912,2840,2960],[4720,5548,784,904],[5548,5688,784,2948],[4720,5548,2836,2948]],
                             'X4.man.tables':[[288,1068,196,316],[1304,1568,368,736],[212,1004,2140,2260],[2156,2425,2134,2255],[1432,1704,2144,2264],[4108,4372,1045,1985]],
                             'X8.man.tables':[[1992,3904,1024,1188],[1300,1828,2528,2700]]},
                        '6':{'Diagonal.Seats':[[624,2007,348,492]],
                             'Cubicle.seats':[[144,519,300,507], [1614,1986,675,1356]],
                             'Windowed.Seats':[[150,2292,63,159],[2250,2355,267,1404] ,[1803,2283,1491,1587]]},
                        '6Chinese':{'Diagonal.Seats':[[610,2342,918,1084]],
                                    'Cubicle.seats':[[710,2644,1252,1340]],
                                    'Windowed.Seats':[[208,300,756,1314],[630,2860,2022,2100],[2982,3074,1022,1992]]}}

#dummy data for occupancy by seat types
student_occupancy = {'Windowed.Seats':30, 'X4.man.tables':20,'X8.man.tables':80}

# Example usage:
region = {'Windowed.Seats':[[36 ,1220,40,132],[40, 128,136,1308],[144,1224,1212,1304],[1644,4532,780,900],[1912,2668,2396,2528],[44,1912,2840,2960],[4720,5548,784,904],[5548,5688,784,2948],[4720,5548,2836,2948]],
                             'X4.man.tables':[[288,1068,196,316],[1304,1568,368,736],[212,1004,2140,2260],[2156,2425,2134,2255],[1432,1704,2144,2264],[4108,4372,1045,1985]],
                             'X8.man.tables':[[1992,3904,1024,1188],[1300,1828,2528,2700]]}
student_occupancy = {'Windowed.Seats':30, 'X4.man.tables':20,'X8.man.tables':80}

image_path = 'floorplan_images/L5_grayscale_image.jpg'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get_time_level', methods=['POST'])
def check_occupancy():
    time = int(request.form.get('time'))
    level = request.form.get('level')
    week = request.form.get('week')
    day = int(request.form.get('day'))
    
    # Replace the following with the logic to fetch occupancy rate and generate visualizations
    occupancy_rate = calculate_occupancy_rate(time, level)
    #visualization = generate_visualization(occupancy_rate)

    total_occupancy = calculate_total_occupancy(df, level, time, week)
    contour_plot = generate_floorplan_contour(image_path, region, student_occupancy)

    # Save the contour plot as a PNG image in memory
    img_buf = io.BytesIO()
    contour_plot.savefig(img_buf, format='png')
    img_buf.seek(0)

    # Encode the image as base64
    import base64
    img_base64 = base64.b64encode(img_buf.read()).decode()

    return render_template('floor_view.html', result=occupancy_rate, time=time, level=level, total_occupancy=total_occupancy, week=week, day=day, plot=img_base64)
@app.route('/overall_view')
def overall_view():
    timing = request.form.get('time')
    level = request.form.get('level')
    floor_data = [
        {'floor': "Level 3", 'occupancy': 60},
        { 'floor': "Level 4", 'occupancy': 80 },
        { 'floor': "Level 5", 'occupancy': 70 },
        { 'floor': "Level 6", 'occupancy': 90 },
        { 'floor': "Level 6 (Chinese Library)", 'occupancy': 75 }
    ]
    circles=[]
    for data in floor_data:
        circle_size = data['occupancy']*2

        circle=pltly.Scatter(
            x=[0],
            y=[0],
            mode='markers',
            marker=dict(size=circle_size, color='red'),
            hoverinfo='text',
            hovertext=f'{data["floor"]}<br>Occupancy: {data["occupancy"]}%'
        )
        circles.append(circle)

    figure = plotly.Figure(data=circles)
    circle_divs = [f.to_html(full_html=False) for f in figure.to_dict()["data"]]

    return render_template('overall_view.html', circle_divs=circle_divs)

@app.route('/floor/<floor>')
def floor_view(floor):
    floor = request.form.get('floor')

    return render_template('floor_view.html', floor=floor)

def calculate_occupancy_rate(timing, level):
    # Replace this with the occupancy rate calculation logic
    return f'Occupancy rate for Level {level} at {timing} is not sure'  # Replace with actual data

def calculate_total_occupancy(df,level,time,week):
    # Filter the DataFrame based on the parameters, replace for more filters
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]

    # Calculate the total occupancy for the filtered data
    occupancy = filtered_df['occupancy'].sum()
    return occupancy

if __name__ == '__main__':
    app.run(debug=True)


