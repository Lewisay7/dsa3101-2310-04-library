from flask import Flask, render_template, request
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import plotly as pltly
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import cv2
from output1 import generate_floorplan_contour


images_path = {'3': "floorplan_images/L_3.png",
               '4':"floorplan_images/L_4.jpg",
               '5': 'floorplan_images/L_5.jpg',
               '6':"floorplan_images/L_6.jpg",
               '6Chinese':"floorplan_images/L_6C.jpg"}

greyscale_images = {'3': "floorplan_images/L3_grayscale_image.jpg",
               '4':"floorplan_images/L4_grayscale_image.jpg",
               '5': 'floorplan_images/L5_grayscale_image.jpg',
               '6':"floorplan_images/L6_grayscale_image.jpg",
               '6Chinese':"floorplan_images/L6C_grayscale_image.jpg"}

regions_coordinates = {'3':{'Discussion.Cubicles':[[991,1311,120,178],[1036,1288,556,610]],
                            'Soft.seats':[[469,855,153,289],[423,852,42,81],[4356,5467,192,330],[1077,1305,40,79],[1075,1305,694,727]],
                            'Moveable.seats':[[1050,1287,250,502]]},
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


app = Flask(__name__, static_url_path='/', static_folder='templates')

# Load dataset
csv_file_path = 'datasets/model_output.csv'
df = pd.read_csv(csv_file_path)

@app.route('/')
def index():
    return render_template('home.html')

#Check occupancy button on home page and on floor_view page
@app.route('/get_time_level', methods=['POST'])
def check_occupancy():
    time = int(request.form.get('time'))
    level = request.form.get('level')
    week = request.form.get('week')
    day = int(request.form.get('day'))

    #total occupancy for all floors
    total_occupancy = calculate_total_occupancy(df, level, time, week,day)

    #occupancy by seat types by floor
    form_seat_types_occupancy(df, level,time,week,day)

    # Three different graphs, comment out the ones you don't want
    occupancy_by_time(level, time, week, day)
    occupancy_by_level(time, week, day)
    occupancy_by_seat(level, time, week, day)

    #heatmap plot

    region = regions_coordinates[level]
    students = form_seat_types_occupancy(df,level,time,week,day)
    image_path = greyscale_images[level]
    image = cv2.imread(image_path)
    heatmap_floor = generate_floorplan_contour(image, region, students)
    

    return render_template('floor_view.html',  time=time, level=level, total_occupancy=total_occupancy, week=week, day=day)


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

def form_seat_types_occupancy(df, level,time,week,day):
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    seat_type = {}
    for i in range(filtered_df.shape[0]):
        seat = filtered_df.iloc[i]['seat_type']
        number = filtered_df.iloc[i]['occupancy']
        seat_type[seat] = number
    return seat_type


def calculate_total_occupancy(df,level,time,week,day):
    # Filter the DataFrame based on the parameters, replace for more filters
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    # Calculate the total occupancy for the filtered data
    occupancy = filtered_df['occupancy'].sum()
    return occupancy


# Generate barplot of Occupancy over time for a specific week, day and level
def occupancy_by_time(level, time, week, day):
    plot1y = []
    plot1x = []
    col = []

    # Calculate occupancy across the day, add color red to current hour
    for i in range(9,22):
        filtered_df = df[(df['level'] == level) & (df['hour'] == i) & (df["week"] == week) &(df["day"] == day) ]
        # Calculate the total occupancy for the filtered data
        fil = filtered_df['occupancy'].sum()
        plot1y.append(fil)
        plot1x.append(i)
        if i == time:
            col.append("red")
        else:
            col.append("black")

    # Plot graph
    fig = go.Figure(data=go.Bar(x=plot1x, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=34),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title=dict(text = 'Occupancy', font=dict(size=30)),plot_bgcolor='white')
    new_tick_values = ["9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]
    fig.update_xaxes(type='category', tickmode='array', tickvals=plot1x, ticktext=new_tick_values,tickfont=dict(size=30))
    fig.update_yaxes(tickfont=dict(size=20))
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=24, color='black')
    ,marker_color=col)

    fig.write_html("templates/occupancy_by_time.html")
    #fig.show()

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

    fig.write_html("templates/occupancy_by_level.html")
    #fig.show()

# Generate a barplot of Occupancy by seats at a specific level
def occupancy_by_seat(level, time, week, day):
    plot1y = []
    x_names= []
    colors = ['#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C']

    #Find seat types for current level
    list1 = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    seat_filter = pd.Series(list1["seat_type"]).drop_duplicates().tolist()
    print(seat_filter)
    print

    #Give nicer names to current seat types
    seat_names = {"Discussion.Cubicles": "Discussion Cubicles", "Soft.seats" : "Soft Seats", "Moveable.seats": "Moveable Seats",
                  "Sofa":"Sofa","Windowed.Seats":"Windowed Seats","X4.man.tables":"4 Man Tables","X8.man.tables":"8 Man Tables",
                  "Diagonal.Seats": "Diagonal Seats","Cubicle.seats":"Cubicle Seats"}
    
    #Find occupancy by seat types
    for i in seat_filter:
        filtered_df = list1[(df['seat_type'] == i) ]
        # Calculate the total occupancy for the filtered data
        fil = filtered_df['occupancy'].sum()
        plot1y.append(fil)
        #Retrieve nicer name format from dictionary
        x_names.append(seat_names.get(i))

    # Plot graph
    fig = go.Figure(data=go.Bar(x=seat_filter, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=34),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title=dict(text = 'Occupancy', font=dict(size=30)),plot_bgcolor='white')
    new_tick_values = x_names
    fig.update_xaxes(type='category', tickmode='array', tickvals=seat_filter, ticktext=new_tick_values,tickfont=dict(size=30))
    fig.update_yaxes(tickfont=dict(size=20))
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=24, color='black')
    ,marker_color=colors)

    fig.write_html("templates/occupancy_by_seat.html")
    #fig.show()

if __name__ == '__main__':
    app.run(debug=True)


