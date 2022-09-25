#heroku specific imports.
from flask import Flask
import os
ON_HEROKU = os.environ.get('ON_HEROKU')
app = Flask(__name__)

# regarding the emoticons.
import demoji
def replace_emojis(tweet):
  emojis = demoji.findall(tweet) 
  for item in emojis:
    tweet = tweet.replace(item,emojis[item]) 
  return tweet

#imports bird_list_df 
import pickle 
def load_all_birds_list():
  file = open("bird_list_df",'rb')
  bird_list_df = pickle.load(file)
  try: 
    return bird_list_df
  except:
    print("Error: No bird list found.")
    return 0
wikibirds = load_all_birds_list() 




@app.route('/') 
def hello_world():
  return "Hello World"


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port = port) 
    #app.run()  # If address is in use, may need to terminate other sessions:
               # Runtime > Manage Sessions > Terminate Other Sessions
      

