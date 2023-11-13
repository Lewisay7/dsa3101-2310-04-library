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


# Your existing Flask app
app = Flask(__name__, static_url_path='/', static_folder='templates')

# Load dataset
csv_file_path = 'datasets/model_output.csv'
df = pd.read_csv(csv_file_path)

# Create a Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')
#app = Dash(__name__)
#server = app.server

# Load dataset
csv_file_path = 'datasets/model_output.csv'
df = pd.read_csv(csv_file_path)

## predefined inputs
images_path = {'3': "floorplan_images/L3_grayscale_downsized.jpg",
               '4':"floorplan_images/L4_grayscale_downsized.jpg",
               '5': 'floorplan_images/L5_grayscale_downsized.jpg',
               '6':"floorplan_images/L6_grayscale_downsized.jpg",
               '6Chinese':"floorplan_images/L6C_grayscale_image.jpg"}

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
    dcc.Dropdown(
        id='level-dropdown',
        options=[
            {'label': 'Level 3', 'value': '3'},
            {'label': 'Level 4', 'value': '4'},
            {'label': 'Level 5', 'value': '5'},
            {'label': 'Level 6', 'value': '6'},
            {'label': 'Level 6 (Chinese)', 'value': '6Chinese'}
        ],
        value='3',
        multi=False,
        style={'width': '50%'}
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
        value='1',
        multi=False,
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='hour-dropdown',
        options=[
            {'label': f'{i}am' if i < 12 else f'{i-12}pm' if i > 12 else '12pm', 'value': i} for i in range(9, 22)
        ],
        value=9,
        multi=False,
        style={'width': '50%'}
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
        style={'width': '50%'}
    ),
    dcc.Graph(id='occupancy-by-time'),
    dcc.Graph(id='occupancy-by-level'),
    dcc.Graph(id='occupancy-by-seat'),
])

@dash_app.callback(
    [Output('occupancy-by-time', 'figure'),
     Output('occupancy-by-level', 'figure'),
     Output('occupancy-by-seat', 'figure')],
    [Input('level-dropdown', 'value'),
     Input('week-dropdown', 'value'),
     Input('hour-dropdown', 'value'),
     Input('day-dropdown', 'value')]
)
def update_all_graphs(selected_level, selected_week, selected_hour, selected_day):
    fig_time = occupancy_by_time(selected_level, selected_hour, selected_week, selected_day)
    fig_level = occupancy_by_level(selected_hour, selected_week, selected_day)
    fig_seat = occupancy_by_seat(selected_level, selected_hour, selected_week, selected_day)
    
    return fig_time, fig_level, fig_seat

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

    return render_template('floor_view.html',  time=time, level=level, total_occupancy=total_occupancy, week=week, day=day)


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

    return fig

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

    return fig



if __name__ == '__main__':
    app.run(debug=True, port=5050)


