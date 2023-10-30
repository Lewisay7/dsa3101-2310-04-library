from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get_time_level', methods=['POST'])
def check_occupancy():
    timing = request.form.get('time')
    level = request.form.get('level')
    
    # Perform any processing or checks here and return a response
    result = f'You entered timing: {timing}, level: {level}'  # Replace with your logic

    return render_template('floor.html', result=result)

if __name__ == 'main':
    app.run(debug=True)

