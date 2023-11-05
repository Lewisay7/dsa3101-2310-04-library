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

    return render_template('floor.html', result=occupancy_rate, time = time, level = level, total_occupancy = total_occupancy, week=week, day=day)

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