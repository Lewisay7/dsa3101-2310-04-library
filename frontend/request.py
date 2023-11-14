from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import plotly as pltly
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import cv2
from heatmap import *
import plotly.subplots as sp


images_path = {'3': "floorplan_images/L3_grayscale_downsized.jpg",
               '4':"floorplan_images/L4_grayscale_downsized.jpg",
               '5': 'floorplan_images/L5_grayscale_downsized.jpg',
               '6':"floorplan_images/L6_grayscale_downsized.jpg",
               '6Chinese':"floorplan_images/L6C_grayscale_downsized.jpg"}

regions_coordinates = {'3':{'Discussion.Cubicles':[[1137,1409,509,566],[1088,1439,114,168]],
                            'Soft.seats':[[467,933,41,66],[521,929,143,266],[1184,1431,632,662],[1185,1431,41,72]],
                            'Moveable.seats':[[1149,1406,233,464]]},
                       '4':{'Soft.seats':[[309,429,149,252],[579,698,268,378],[855,1004,171,200],[1224,1340,363,557],[1190,1353,623,636]],
                             'Sofa':[[278,462,300,350], [768, 1052,299,348]]},
                       '5':{'Windowed.Seats':[[12 ,323,9,29],[9,36,29,287],[38,323,264,285],[432,1194,171,197],[11,506,620,648],[507,701,525,549],[1244,1464,620,645],[1464,1499,198,623],[1242,1499,171,194]],
                             'X4.man.tables':[[80,281,42,71],[59,266,468,497],[344,413,80,158],[380,449,471,495],[569,638,470,495],[1182,1152,228,435]],
                             'X8.man.tables':[[528,1029,224,260],[348,482,557,580]]},
                        '6':{'Diagonal.Seats':[[390,485,147,209],[590,687,147,209],[786,882,147,209],[971,1067,147,209],[1155,1250,147,209]],
                             'Cubicle.seats':[[92,327,129,216], [387,1229,93,122],[1007,1239,288,578]],
                             'Windowed.Seats':[[95,1427,27,68],[1403,1467,114,599] ,[1124,1425,635,678]]},
                        '6Chinese':{'Diagonal.Seats':[[281,372,285,339],[464,555,285,339],[638,729,285,339],[819,909,285,339],[992,1082,285,339]],
                                    'Cubicle.seats':[[324,1217,390,419]],
                                    'Windowed.Seats':[[96,138,239,407],[1377,1422,320,620],[291,1296,632,659]]}}

actual_seat_count = {'3':{'Discussion.Cubicles':56,
                            'Soft.seats':132,
                            'Moveable.seats':156},
                       '4':{'Soft.seats':268,
                             'Sofa':32},
                       '5':{'Windowed.Seats':97,
                             'X4.man.tables':220,
                             'X8.man.tables':160},
                        '6Chinese':{'Diagonal.Seats':72,
                             'Cubicle.seats':52,
                             'Windowed.Seats':36},
                        '6C':{'Diagonal.Seats':92,
                                    'Cubicle.seats':155,
                                    'Windowed.Seats':136}}

#nicer seat names
seat_names = {"Discussion.Cubicles": "Discussion Cubicles", "Soft.seats" : "Soft Seats", "Moveable.seats": "Moveable Seats",
                  "Sofa":"Sofa","Windowed.Seats":"Windowed Seats","X4.man.tables":"4 Man Tables","X8.man.tables":"8 Man Tables",
                  "Diagonal.Seats": "Diagonal Seats","Cubicle.seats":"Cubicle Seats"}
    
app = Flask(__name__, static_url_path='/', static_folder='templates')

# Load dataset
csv_file_path = '../datasets/model_output.csv'
actual_seat_path = '../datasets/actual_seat_count.csv'
df = pd.read_csv(csv_file_path)
seat_df = pd.read_csv(actual_seat_path)

@app.route('/')
def index():
    return render_template('home.html')

#Check occupancy button on home page and on floor_view page
# @app.route('/get_time_level', methods=['POST'])
# def check_occupancy():
#     time = int(request.form.get('time'))
#     level = request.form.get('level')
#     week = request.form.get('week')
#     day = int(request.form.get('day'))

#     #total occupancy for all floors
#     total_occupancy = calculate_total_occupancy(df, level, time, week,day)

#     #occupancy by seat types by floor
#     form_seat_types_occupancy(df, level,time,week,day)

#     # Three different graphs, comment out the ones you don't want
#     # occupancy_by_time(level, time, week, day)
#     # occupancy_by_level(time, week, day)
#     # occupancy_by_seat(level, time, week, day)

#     # region = regions_coordinates[level]
#     # students = form_seat_types_occupancy(df,level,time,week,day)
#     # image_path = images_path[level]
#     # image = cv2.imread(image_path)
#     # heatmap_floor = generate_floorplan_contour(image_path, region, students)
    

#     return render_template('floor_view.html',  time=time, level=level, total_occupancy=total_occupancy, week=week, day=day)


@app.route('/get_time_overall', methods=['POST'])
def overall():
    level = {'3','4','5','6','6Chinese'}
    week = request.form.get('week')
    time = int(request.form.get('time'))
    day = int(request.form.get('day'))

    occupancy_by_level(time, week, day)

    #generating heatmaps for all floor
    for i in level:
        generate_heatmap(i,week,time,day)
    
    #total occupancy for all floors
    total_occupancy = calculate_total_occupancy(df, level, time, week,day)

    return render_template('overall_view.html',  time=time, level=level, total_occupancy=total_occupancy, week=week, day=day)



def calculate_total_occupancy(df,level,time,week,day):
    if level == "overall":
        filtered_df = df[(df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
        occupancy = filtered_df['occupancy'].sum()
        return occupancy
    # Filter the DataFrame based on the parameters, replace for more filters
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    # Calculate the total occupancy for the filtered data
    occupancy = filtered_df['occupancy'].sum()

    return occupancy

def form_seat_types_occupancy(df, level,time,week,day):
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    seat_type = {}
    for i in range(filtered_df.shape[0]):
        seat = filtered_df.iloc[i]['seat_type']
        number = filtered_df.iloc[i]['occupancy']
        seat_type[seat] = number
    return seat_type



# Generate a barplot of Occupancy by Level
def occupancy_by_level(time, week, day):
    plot1y = []
    plot1x = [3, 4, 5, 6, 7]
    colors = ['#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C']

    # Get Occupancy by level 
    for i in range(3,8):
        x = str(i)
        if i == 7:
            x = "6Chinese"
        fil = calculate_total_occupancy(df, x, time, week,day)
        plot1y.append(fil)

    # Plot graph
    fig = go.Figure(data=go.Bar(x=plot1x, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=34),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title=dict(text = 'Occupancy', font=dict(size=30)),plot_bgcolor='white')
    new_tick_values = ["Level 3", "Level 4", "Level 5", "Level 6", "Level 6 Chinese"]
    fig.update_xaxes(type='category', tickmode='array', tickvals=plot1x, ticktext=new_tick_values,tickfont=dict(size=30))
    fig.update_yaxes(tickfont=dict(size=20))
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=24, color='black')
    ,marker_color=colors)

    fig.write_html("./templates/overall_plots/occupancy_by_level.html")

# Generate heatmaps of all level
def generate_heatmap(level, week, hour, day):
    region = regions_coordinates[level]
    students = form_seat_types_occupancy(df, level, hour, week, day)
    image_path = images_path[level]
    heatmap_fig = generate_floorplan_contour_html(image_path, region, students,level,seat_names,actual_seat_count)
    return heatmap_fig



if __name__ == '__main__':
    app.run(debug=True, port= 5050)


