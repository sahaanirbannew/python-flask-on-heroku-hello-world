#heroku specific imports.
from flask import Flask
import os
ON_HEROKU = os.environ.get('ON_HEROKU')
app = Flask(__name__)






@app.route('/') 
def hello_world():
  return "Hello World"


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port = port) 
    #app.run()  # If address is in use, may need to terminate other sessions:
               # Runtime > Manage Sessions > Terminate Other Sessions
      

