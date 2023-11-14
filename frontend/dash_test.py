import math
from flask import Flask, render_template, request
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import plotly as pltly
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import cv2
from dash import Dash, dcc, html, Input, Output
from heatmap import *
import plotly.subplots as sp


# Your existing Flask app
app = Flask(__name__, static_url_path='/', static_folder='templates')


# Create a Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')
#app = Dash(__name__)
#server = app.server

# Load dataset
csv_file_path = '../datasets/model_output.csv'
df = pd.read_csv(csv_file_path)
actual_seat_path = '../datasets/actual_seat_count.csv'
seat_df = pd.read_csv(actual_seat_path)
## predefined inputs
"""time_dict = {'label': f'{i}am' if i < 12 else f'{i-12}pm' if i > 12 else '12pm', 'value': i} for i in range(9, 22)
time_mapping = {i: f"{i % 12 or 12} {'AM' if i < 12 else 'PM'}" for i in range(1, 25)}
print(time_mapping.get(4))
print(time_mapping.get(12))
print(time_mapping.get(24))"""
images_path = {'3': "floorplan_images/L3_grayscale_downsized.jpg",
               '4':"floorplan_images/L4_grayscale_downsized.jpg",
               '5': 'floorplan_images/L5_grayscale_downsized.jpg',
               '6':"floorplan_images/L6_grayscale_downsized.jpg",
               '6Chinese':"floorplan_images/L6C_grayscale_downsized.jpg"}

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
                        '6':{'Diagonal.Seats':92,
                                    'Cubicle.seats':155,
                                    'Windowed.Seats':136}}

regions_coordinates = {'3':{'Discussion.Cubicles':[[1137,1409,509,566],[1088,1439,114,168]],
                            'Soft.seats':[[467,933,41,66],[521,929,143,266],[1184,1431,632,662],[1185,1431,41,72]],
                            'Moveable.seats':[[1149,1406,233,464]]},
                       '4':{'Soft.seats':[[309,429,149,252],[579,698,268,378],[855,1004,171,200],[1224,1340,363,557],[1190,1353,623,636]],
                             'Sofa':[[278,462,300,350], [768, 1052,299,348]]},
                       '5':{'Windowed.Seats':[[12 ,323,9,29],[9,36,29,287],[38,323,264,285],[432,1194,171,197],[11,506,620,648],[507,701,525,549],[1244,1464,620,645],[1464,1499,198,623],[1242,1499,171,194]],
                             'X4.man.tables':[[80,281,42,71],[59,266,468,497],[344,413,80,158],[380,449,471,495],[569,638,470,495],[1083,1152,228,435]],
                             'X8.man.tables':[[528,1029,224,260],[348,482,557,580]]},
                        '6':{'Diagonal.Seats':[[390,485,147,209],[590,687,147,209],[786,882,147,209],[971,1067,147,209],[1155,1250,147,209]],
                             'Cubicle.seats':[[92,327,129,216], [387,1229,93,122],[1007,1239,288,578]],
                             'Windowed.Seats':[[95,1427,27,68],[1403,1467,114,599] ,[1124,1425,635,678]]},
                        '6Chinese':{'Diagonal.Seats':[[281,372,285,339],[464,555,285,339],[638,729,285,339],[819,909,285,339],[992,1082,285,339]],
                                    'Cubicle.seats':[[324,1217,390,419]],
                                    'Windowed.Seats':[[96,138,239,407],[1377,1422,320,620],[291,1296,632,659]]}}
seat_names = {"Discussion.Cubicles": "Discussion Cubicles", "Soft.seats" : "Soft Seats", "Moveable.seats": "Moveable Seats",
                  "Sofa":"Sofa","Windowed.Seats":"Windowed Seats","X4.man.tables":"4 Man Tables","X8.man.tables":"8 Man Tables",
                  "Diagonal.Seats": "Diagonal Seats","Cubicle.seats":"Cubicle Seats"}



dash_app.layout = html.Div([
    # First Row
    html.Div([
        # Stacked dropdowns
        html.Div([
            dcc.Dropdown(
                id='level-dropdown',
                options=[
                    {'label': 'Level 3', 'value': '3'},
                    {'label': 'Level 4', 'value': '4'},
                    {'label': 'Level 5', 'value': '5'},
                    {'label': 'Level 6', 'value': '6'},
                    {'label': 'Level 6 (Chinese)', 'value': '6Chinese'}
                ],
                value="3",
                multi=False,
                style={'width': '100%', 'margin-bottom': '10px'}
            ),
            dcc.Dropdown(
                id='week-dropdown',
                options=[
                    {'label': 'Week 1', 'value': '1'},
                    {'label': 'Week 2', 'value': '2'},
                    {'label': 'Week 3', 'value': '3'},
                    {'label': 'Week 4', 'value': '4'},
                    {'label': 'Week 5', 'value': '5'},
                    {'label': 'Week 6', 'value': '6'},
                    {'label': 'Week 7', 'value': '7'},
                    {'label': 'Week 8', 'value': '8'},
                    {'label': 'Week 9', 'value': '9'},
                    {'label': 'Week 10', 'value': '10'},
                    {'label': 'Week 11', 'value': '11'},
                    {'label': 'Week 12', 'value': '12'},
                    {'label': 'Week 13', 'value': '13'},
                    {'label': 'Exam Week', 'value': 'Exam'},
                    {'label': 'Reading Week', 'value': 'Reading'},
                    {'label': 'Recess week', 'value': 'Recess'}
                ],
                value="1",
                multi=False,
                style={'width': '100%', 'margin-bottom': '10px'}
            ),
            dcc.Dropdown(
                id='hour-dropdown',
                options=[
                    {'label': f'{i}am' if i < 12 else f'{i-12}pm' if i > 12 else '12pm', 'value': i} for i in range(9, 22)
                ],
                value=9,
                multi=False,
                style={'width': '100%', 'margin-bottom': '10px'}
            ),
            dcc.Dropdown(
                id='day-dropdown',
                options=[
                    {'label': 'Monday', 'value': 1},
                    {'label': 'Tuesday', 'value': 2},
                    {'label': 'Wednesday', 'value': 3},
                    {'label': 'Thursday', 'value': 4},
                    {'label': 'Friday', 'value': 5},
                    {'label': 'Saturday', 'value': 6},
                    {'label': 'Sunday', 'value': 7}
                ],
                value=1,
                multi=False,
                style={'width': '100%', 'margin-bottom': '10px'}
            ),
        ], style={'width': '15%', 'margin-right': '20px', 'padding': '20px','margin-right': '15px'}),  # Stacked dropdowns with some styling

        # Graphs
        html.Div([
            dcc.Graph(id='occupancy-by-time', style={'width': '30%', 'height': '400px', 'border': '4px solid black', 'margin-right': '15px'}),
            dcc.Graph(id='occupancy-by-level', style={'width': '30%', 'height': '400px', 'border': '4px solid black', 'margin-right': '15px'}),
            dcc.Graph(id='occupancy-by-seat', style={'width': '30%', 'height': '400px', 'border': '4px solid black'}),
        ], style={'width': '85%', 'display': 'flex', 'flex-wrap': 'wrap'}),  # Graphs with flex wrap to handle responsive layout
    ], style={'display': 'flex', 'margin-bottom': '60px'}),

    # Second Row
    html.Div([
        # Graphs with spacing
        html.Div([
            dcc.Graph(id='occupancy-by-level-pie', style={'width': '30%', 'height': '400px', 'margin-right': '60px'}),
            dcc.Graph(id='heatmap', style={'width': '70%', 'height': '600px', 'border': '4px solid black'}),
        ], style={'display': 'flex', 'margin-bottom': '30px'}),
    ]),
])

@dash_app.callback(
    [Output('occupancy-by-time', 'figure'),
     Output('occupancy-by-level', 'figure'),
     Output('occupancy-by-seat', 'figure'),
     Output('heatmap', 'figure'),
     Output('occupancy-by-level-pie', 'figure')],  # Add the pie chart output
    [Input('level-dropdown', 'value'),
     Input('week-dropdown', 'value'),
     Input('hour-dropdown', 'value'),
     Input('day-dropdown', 'value')]
)
def update_all_graphs(selected_level, selected_week, selected_hour, selected_day):
    fig_time = occupancy_by_time(selected_level, selected_hour, selected_week, selected_day)
    fig_level = occupancy_by_level(selected_hour, selected_week, selected_day)
    fig_seat = occupancy_by_seat(selected_level, selected_hour, selected_week, selected_day)
    pie_chart = occupancy_level_pie(selected_level,selected_hour,selected_week,selected_day)

    # Generate heatmap using the new function
    heatmap_fig = generate_heatmap_fig(selected_level, selected_week, selected_hour, selected_day)
    
    return fig_time, fig_level, fig_seat, heatmap_fig, pie_chart

@app.route('/')
def index():
    return render_template('home.html')

#Check occupancy button on home page and on floor_view page
@app.route('/get_time_level', methods=['POST'])
def check_occupancy():
    level = request.form.get('level')
    week = request.form.get('week')
    time = int(request.form.get('time'))
    day = int(request.form.get('day'))

    #total occupancy for all floors
    total_occupancy = calculate_total_occupancy(df, level, time, week,day)

    return render_template('floor_view.html')

@app.route('/get_time_overall', methods=['POST'])
def overall():
    level = {'3','4','5','6','6Chinese'}
    week = request.form.get('week')
    time = int(request.form.get('time'))
    day = int(request.form.get('day'))

    overall_occupancy_by_level(time, week, day)
    rate_by_level(time,week,day)

    #generating heatmaps for all floor
    for i in level:
        generate_heatmap(i,week,time,day)
    
    #total occupancy for all floors
    df = pd.read_csv(csv_file_path)
    seat_df = pd.read_csv(actual_seat_path)
    time_string = str(time)
    day_string = str(day)
    days = {'1': 'Monday', '2':'Tuesday', '3':'Wednesday', '4':'Thursday', '5': 'Friday', '6': 'Saturday', '7':' Sunday'}
    timing = {'1':"1 am", '2':"2 am",'3':"3 am",'4':"4 am",'5':"5 am",'6':"6 am",'7':"7 am",'8':"8 am",'9':"9 am",'10':"10 am",'11':"11 am",'12':"12 pm",
              '13':"1 pm",'14':"2 pm",'15':"3 pm",'16':"4 pm",'17':"5 pm",'18':"6 pm",'19':"7 pm",'20':"8 pm",'21':"9 pm",'22':"10 pm",'23':"11 pm",'24':"12 am"}
    total_occupancy = overall_occupancy(df,time, week,day)
    total_rate = overall_occupancy_rate(df, seat_df,time,week,day)

    return render_template('overall_view.html',day = days.get(day_string), time = timing.get(time_string), week = week, total_occupancy = total_occupancy, total_rate = total_rate)


#total number of students for all floor
def overall_occupancy(df,time,week,day):
    filtered_df = df[(df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    occupancy = filtered_df['occupancy'].sum()
    return occupancy

# total number of students of each floor 
def level_total_occupancy(df,level,time,week,day):
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

#function to calculate the overall occupancy rate of the library
def overall_occupancy_rate(df, seat_df, time, week,day):
    occupancy = overall_occupancy(df,time,week,day)
    total_seats = 0
    for i in range(seat_df.shape[0]):
        total_seats += seat_df.iloc[i]['count']
    total_rate = round(occupancy/total_seats,2)*100
    return total_rate
    
#function to get a dictionary containing capacity by floor
## {'3': 344, '4': 300, '5': 477, '6Chinese': 160, '6': 383}
def capacity_by_floor(seat_df):
    capacity = {}
    for i in range(seat_df.shape[0]):
        if seat_df.iloc[i]['level'] not in capacity:
            capacity[seat_df.iloc[i]['level']] = 0
        capacity[seat_df.iloc[i]['level']] +=  seat_df.iloc[i]['count']
    return capacity 

# Generate a barplot of number of students by Level
def overall_occupancy_by_level(time, week, day):
    plot1y = []
    plot1x = [3, 4, 5, 6, 7]
    colors = ['#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C']

    # Get Occupancy by level 
    for i in range(3,8):
        x = str(i)
        if i == 7:
            x = "6Chinese"
        fil = level_total_occupancy(df, x, time, week,day)
        plot1y.append(fil)

    # Plot graph
    fig = go.Figure(data=go.Bar(x=plot1x, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=20),textfont_size=20))
    # Add labels and title
    fig.update_layout(  xaxis_title="", 
                        yaxis_title=dict(text = 'Occupancy', font=dict(size=20)),
                        autosize=True,
                        margin=dict(l=0, r=0, t=60 , b=30),paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    new_tick_values = ["Level 3", "Level 4", "Level 5", "Level 6", "Level 6 C"]
    fig.update_xaxes(type='category', 
                     tickmode='array', 
                     tickvals=plot1x, 
                     ticktext=new_tick_values,
                     tickfont=dict(size=15))
    fig.update_yaxes(tickfont=dict(size=10))
    fig.update_traces(textposition='outside',  
                      textfont=dict(size=15, color='black'),
                      marker_color=colors)
    fig.write_html("./templates/overall_plots/occupancy_by_level.html")

#generate a horizontal bar plot of occupancy rates by level
def rate_by_level(time, week, day):
    plot1y = []
    plot1x = [3, 4, 5, 6, 7]
    colors = ['#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C']

    # Get Occupancy by level
    for i in range(3, 8):
        x = str(i)
        if i == 7:
            x = "6Chinese"
        fil = round(level_total_occupancy(df, x, time, week, day) / capacity_by_floor(seat_df)[x], 2)
        plot1y.append(fil)

    # Format the text with percentage and customize hover text
    text_data = [f"{occupancy_rate * 100:.2f}%" for occupancy_rate in plot1y]
    hover_text = [f"Level {level}<br>Occupancy Rate: {occupancy_rate * 100:.2f}%" for level, occupancy_rate in zip(plot1x, plot1y)]
    fig = go.Figure(data=go.Bar(y=plot1x, x=plot1y, text=text_data, hovertext=hover_text, textposition='outside',
                                textfont=dict(size=20), textfont_size=20, orientation='h', hovertemplate="%{hovertext}"))
    

    fig.update_layout(
        yaxis_title="",
        xaxis_title=dict(text='Occupancy Rate', font=dict(size=30)),
        autosize = True,
        margin=dict(l=0, r=0, t=0 , b=0),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    new_tick_values = ["Level 3", "Level 4", "Level 5", "Level 6", "Level 6 C"]
    fig.update_yaxes(type='category', tickmode='array', tickvals=plot1x, ticktext=new_tick_values,
                     tickfont=dict(size=15))
    fig.update_xaxes(tickfont=dict(size=1))
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=15, color='black'),
        marker_color=colors
    )

    fig.write_html("./templates/overall_plots/rate_by_level.html")

# Generate heatmaps of all level
def generate_heatmap(level, week, hour, day):
    region = regions_coordinates[level]
    students = form_seat_types_occupancy(df, level, hour, week, day)
    image_path = images_path[level]
    heatmap_fig = generate_floorplan_contour_html(image_path, region, students,level,seat_names,actual_seat_count)
    return heatmap_fig

def generate_heatmap_fig(level, week, hour, day):
    region = regions_coordinates[level]
    students = form_seat_types_occupancy(df, level, hour, week, day)
    image_path = images_path[level]
    heatmap_fig = generate_floorplan_contour(image_path, region, students,level,seat_names,actual_seat_count)
    return heatmap_fig

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


# Generate barplot of Occupancy over time for a specific week, day and level
def occupancy_by_time(level, time, week, day):
    plot1y = []
    plot1x = []
    col = []

    # Calculate occupancy across the day, add color red to current hour
    for i in range(9,22):
        if level == "overall":
            filtered_df = df[(df['hour'] == i) & (df["week"] == week) &(df["day"] == day) ]
        else:
            filtered_df = df[(df['level'] == level) & (df['hour'] == i) & (df["week"] == week) &(df["day"] == day) ]
        # Calculate the total occupancy for the filtered data
        fil = filtered_df['occupancy'].sum()
        plot1y.append(fil)
        plot1x.append(i)
        if i == time:
            col.append("red")
        else:
            col.append("black")

    max_y_axis = max(plot1y)*1.2
    # Plot graph
    fig = go.Figure(data=go.Bar(x=plot1x, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=20),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title="", title=dict(text = "<b>"+'Occupancy over Time'+"</b>", font=dict(size=20,)), title_x = 0.5,plot_bgcolor='white',margin=dict(t=50) )
    new_tick_values = ["9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]
    fig.update_xaxes(type='category', tickmode='array', tickvals=plot1x, ticktext=new_tick_values,tickfont=dict(size=15))
    fig.update_yaxes(tickfont=dict(size=15), range = [0, max_y_axis])
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=24, color='black')
    ,marker_color=col)

    return fig

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

    max_y_axis = max(plot1y)*1.2
    # Plot graph
    fig = go.Figure(data=go.Bar(x=plot1x, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=20),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title="", title=dict(text = "<b>"+'Occupancy in each Level'+"</b>", font=dict(size=20,)), title_x = 0.5,plot_bgcolor='white',margin=dict(t=50,b=10) )
    new_tick_values = ["Level 3", "Level 4", "Level 5", "Level 6", "Chinese"]
    fig.update_xaxes(type='category', tickmode='array', tickvals=plot1x, ticktext=new_tick_values,tickfont=dict(size=15))
    fig.update_yaxes(tickfont=dict(size=15), range = [0, max_y_axis])
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=15, color='black')
    ,marker_color=colors)

    return fig

# Generate a barplot of Occupancy by seats at a specific level
def occupancy_by_seat(level, time, week, day):
    plot1y = []
    x_names= []
    colors = ['#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C','#053F5C', '#429EBD', '#9FE7F5', '#F7AD19', '#F27F0C']

    #Find seat types for current level
    if level == "overall":
        list1 = df[(df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    else:
        list1 = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    seat_filter = pd.Series(list1["seat_type"]).drop_duplicates().tolist()
    print(seat_filter)
    print

    #Give nicer names to current seat types
    seat_names = {"Discussion.Cubicles": "Discussion Cubicles", "Soft.seats" : "Soft Seats", "Moveable.seats": "Moveable Seats",
                  "Sofa":"Sofa","Windowed.Seats":"Windowed Seats","X4.man.tables":"4M Tables","X8.man.tables":"8M Tables",
                  "Diagonal.Seats": "Diagonal Seats","Cubicle.seats":"Cubicle Seats"}
    
    #Find occupancy by seat types
    for i in seat_filter:
        filtered_df = list1[(df['seat_type'] == i) ]
        # Calculate the total occupancy for the filtered data
        fil = filtered_df['occupancy'].sum()
        plot1y.append(fil)
        #Retrieve nicer name format from dictionary
        x_names.append(seat_names.get(i))

    max_y_axis = max(plot1y)*1.2
    # Plot graph
    fig = go.Figure(data=go.Bar(x=seat_filter, y=plot1y,text=plot1y, textposition='outside', textfont=dict(size=20),textfont_size=24))
    # Add labels and title
    fig.update_layout( xaxis_title="", yaxis_title="", title=dict(text = "<b>"+'Occupancy by Seat Type'+"</b>", font=dict(size=20,)), title_x = 0.5,plot_bgcolor='white',margin=dict(t=50,b=0) )
    new_tick_values = x_names
    fig.update_xaxes(type='category', tickmode='array', tickvals=seat_filter, ticktext=new_tick_values,tickfont=dict(size=15))
    fig.update_yaxes(tickfont=dict(size=15), range = [0, max_y_axis])
    fig.update_traces(
    textposition='outside',  
    textfont=dict(size=15, color='black')
    ,marker_color=colors)

    return fig

def occupancy_by_level_pie(time,week,day):
    plot1y = []
    label_list = []
    subplot_titles =['Level 3','Level 4','Level 5','Level 6','Level 6 (Chinese']

    max_seat = pd.read_csv('datasets/actual_seat_count.csv')
    # Calculate the total occupancy for the filtered data
    # Get Occupancy by level 
    for i in range(3,8):
        x = str(i)
        if i == 7:
            x = "6Chinese"
        filtered_seat = max_seat[(df['level'] == x)]
        occupancy = filtered_seat['count'].sum()
        fil = calculate_total_occupancy(df, x, time, week,day)
        non_occupied = occupancy-fil
        occupied_vs_non = [fil,non_occupied]
        plot1y.append(occupied_vs_non)
        vslabels = ["Occupied", "Not Occupied"]
        label_list.append(vslabels)


    """labels_list = [['Category A', 'Category B', 'Category C'],
               ['Category X', 'Category Y', 'Category Z']]
    values_list = [[30, 50, 20], [40, 30, 30]]
    subplot_titles = ['Pie Chart 1', 'Pie Chart 2']"""

    fig = sp.make_subplots(rows=1, cols=len(label_list), subplot_titles=subplot_titles, specs=[[{'type':'domain'}]*len(label_list)])

    # Add pie charts to subplots
    for i, (labels, values) in enumerate(zip(label_list, plot1y), start=1):
        fig.add_trace(go.Pie(labels=labels, values=values), 1, i)

    return fig


# Create pie chart for single floor
def occupancy_level_pie(level, time, week, day):
    max_seat = pd.read_csv('datasets/actual_seat_count.csv')
    
    # Calculate the total occupancy for the filtered data
    fil = calculate_total_occupancy(df, level, time, week, day)
    filtered_seat = max_seat[(df['level'] == level)]
    occupancy = filtered_seat['count'].sum()
    non_occupied = occupancy - fil
    occupied_vs_non = [fil, non_occupied]
    vslabels = ["Occupied", "Not Occupied"]

    # Choose a color palette
    colors = ["red", 'blue']

    fig = go.Figure(data=[go.Pie(labels=vslabels, values=occupied_vs_non, marker=dict(colors=colors))])

    # Customize layout
    fig.update_layout(
        title=dict(text = "<b>Total Floor Occupancy: </b>" + "<b>"+str(fil)+"</b>", font=dict(size=20,)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x = 0.5
    )

    # Customize text information on the chart
    fig.update_traces(
        textinfo='percent+label',  # Display percentage and label
        textposition='inside',  # Place text inside the pie
        showlegend = False
    )

    return fig

if __name__ == '__main__':
    app.run(debug = True,port=5050)


