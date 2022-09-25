#heroku specific imports.
from flask import Flask
import os
ON_HEROKU = os.environ.get('ON_HEROKU')
app = Flask(__name__)


#program requirements
import pickle 
#from Levenshtein import distance as levenshtein_distance
import re
#import tweepy
import preprocessor as p
p.set_options(p.OPT.EMOJI, p.OPT.MENTION, p.OPT.URL, p.OPT.SMILEY, p.OPT.NUMBER, p.OPT.HASHTAG)
#import os, sys 
import pandas as pd  
import spacy
import demoji
demoji.download_codes()
nlp = spacy.load("en_core_web_sm")



@app.route('/') 
def hello_world():
  return "Hello World"


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port = port) 
    #app.run()  # If address is in use, may need to terminate other sessions:
               # Runtime > Manage Sessions > Terminate Other Sessions
      

