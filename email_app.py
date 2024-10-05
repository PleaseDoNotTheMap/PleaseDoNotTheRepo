from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    # Get parameters from the URL
    param1 = request.args.get('param1', default='default_value1')
    param2 = request.args.get('param2', default='default_value2')
    param3 = request.args.get('param3', default='default_value3')
    param4 = request.args.get('param4', default='default_value4')
    param5 = request.args.get('param5', default='default_value5')


    # Run the Python script with parameters
    result = subprocess.run(['python3', 'send_notifications.py', param1, param2, param3, param4, param5], capture_output=True, text=True)
    return f"<pre>{result.stdout}</pre>"

if __name__ == '__main__':
    app.run(debug=True)
