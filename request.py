from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import plotly as pltly
import pandas as pd
import plotly.graph_objects as go

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

    # Check output of time, level and total occupancy
    occupancy_rate = calculate_occupancy_rate(time,level)
    total_occupancy = calculate_total_occupancy(df, level, time, week,day)

    # Three different graphs, comment out the ones you don't want
    occupancy_by_time(level, time, week, day)
    occupancy_by_level(time, week, day)
    occupancy_by_seat(level, time, week, day)
    

    return render_template('floor_view.html', result=occupancy_rate, time=time, level=level, total_occupancy=total_occupancy, week=week, day=day)

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
    return f'Occupancy rate for Level {level} at {timing} is not sure'   # Replace with actual data

def calculate_total_occupancy(df,level,time,week,day):
    # Filter the DataFrame based on the parameters, replace for more filters
    filtered_df = df[(df['level'] == level) & (df['hour'] == time) & (df["week"] == week) &(df["day"] == day)]
    # Calculate the total occupancy for the filtered data
    occupancy = filtered_df['occupancy'].sum()
    return occupancy

def generate_visualization(occupancy_rate):
    # Replace this with your visualization generation logic using Matplotlib or Plotly
    # Example: generate a simple bar chart

    levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6']
    occupancy_data = [60, 45, 75, 80, 70, 55]  # Replace with actual data

    plt.bar(levels, occupancy_data)
    plt.xlabel('Levels')
    plt.ylabel('Occupancy Rate')
    plt.title('Occupancy Rate by Level')
    plt.savefig('static/occupancy_plot.png')  # Save the plot as a file
    plt.close()

    return 'occupancy_plot.png'  # Return the filename of the generated plot

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

    fig.show()

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

    fig.show()

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

    fig.show()

if __name__ == '__main__':
    app.run(debug=True)


