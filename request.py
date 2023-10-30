from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import plotly as pltly

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get_time_level', methods=['POST'])
def check_occupancy():
    timing = request.form.get('time')
    level = request.form.get('level')
    
    # Replace the following with the logic to fetch occupancy rate and generate visualizations
    occupancy_rate = calculate_occupancy_rate(timing, level)
    visualization = generate_visualization(occupancy_rate)

    return render_template('floor.html', result=occupancy_rate, visualization=visualization)

def calculate_occupancy_rate(timing, level):
    # Replace this with the occupancy rate calculation logic
    return f'Occupancy rate for Level {level} at {timing} is 60%'  # Replace with actual data

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

