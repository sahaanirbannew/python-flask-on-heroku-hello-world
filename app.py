from flask import Flask
ON_HEROKU = os.environ.get('ON_HEROKU')
app = Flask(__name__)


@app.route('/') 
def hello_world():
  return "Hello World"

port = int(os.environ.get('PORT', 5000))
app.run(debug=True, port = port) 
