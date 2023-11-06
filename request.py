from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import plotly as pltly
import pandas as pd

app = Flask(__name__, static_url_path='/', static_folder='templates')

# Load dataset
csv_file_path = 'datasets/model_output.csv'
df = pd.read_csv(csv_file_path)

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

    # Filter the DataFrame based on the parameters, replace for more filters
    filtered_df = df[(df['level'] == level) & (df['hour'] == time)]

    # Calculate the total occupancy for the filtered data
    total_occupancy = filtered_df['occupancy'].sum()

    return render_template('floor_view.html', result=occupancy_rate, time = time, level = level, total_occupancy = total_occupancy, week=week, day=day)

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

if __name__ == '__main__':
    app.run(debug=True)


