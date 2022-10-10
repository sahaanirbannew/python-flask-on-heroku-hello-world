#heroku specific imports.
from flask import Flask, request, render_template
import os
ON_HEROKU = os.environ.get('ON_HEROKU')
app = Flask(__name__)

#request to get the param
import urllib.request

#for NLP purposes
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

import demoji
import pickle 
import spacy 
import preprocessor as p
import re
import demoji
p.set_options(p.OPT.EMOJI, p.OPT.MENTION, p.OPT.URL, p.OPT.SMILEY, p.OPT.NUMBER, p.OPT.HASHTAG)
from Levenshtein import distance as levenshtein_distance
import requests 
import tweepy

#twitter object
def create_twitter_app_obj():
  consumer_key = "iPaIdR8GRI59yTJMs0Es0dIBN"
  consumer_secret = "pLadg3UaLeK3yKDujRMChRN3p8hUDBOjBsuOBy8j8ERr4zz1vs"
  access_token = "39085479-AabHt6bmFSbClDfUZuHjModYPAxVlOxHeMA79UyVt"
  access_token_secret = "3IqXDISfqg14wzMNNn2AX4KYG9Wfkltt21QxKasE4YNnG" 
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
  auth.set_access_token(access_token, access_token_secret) 
  api = tweepy.API(auth) 
  return api

# regarding the emoticons.
def replace_emojis(tweet):
  emojis = demoji.findall(tweet) 
  for item in emojis:
    tweet = tweet.replace(item," "+emojis[item]+" ") 
  return tweet

#imports bird_list_df 
def load_all_birds_list():
  file = open("bird_list_df",'rb')
  bird_list_df = pickle.load(file)
  try: 
    return bird_list_df
  except: 
    return 0

#imports eBird list
def get_eBird_commonNames_data():
  file = open("bird_dict_comName",'rb')
  try:
    eBird_commonNames_data = pickle.load(file)
    return eBird_commonNames_data 
  except Exception as e: 
    return 0
  
def get_ebirds_list(ebirds): 
  birdnames = [] 
  for bird in ebirds:
    if ebirds[bird].find("/") >-1: birdnames = add_list_birds_to_list_from_curated_list(return_birdnames__mit_slash(ebirds[bird]), birdnames)
    elif len(re.findall(r'\(.+\)', ebirds[bird])) >0: birdnames = add_list_birds_to_list_from_curated_list(get_birdnames__mit_brac(ebirds[bird]), birdnames) 
    else: birdnames = add_single_bird_to_list_from_curated_list(ebirds[bird], birdnames)  
  return birdnames

def add_list_birds_to_list_from_curated_list(list_, birdnames):
  for bird in list_: 
    birdnames = add_single_bird_to_list_from_curated_list(bird, birdnames)
  return birdnames

def return_birdnames__mit_slash(birdname__):
  birdnames_ = []  
  _terms = birdname__.split("/")
  last_elem = _terms[len(_terms)-1].strip().split(" ")[-1:]  
  for term in _terms[:-1]: 
    birdnames_.append(term + " "+last_elem[0]) 
  birdnames_.append(_terms[-1].split(" ")[0] + " "+last_elem[0])  
  return birdnames_ 

def add_single_bird_to_list_from_curated_list(bird, birdnames): 
  birdname____ = basic_preprocess(bird, {})
  if birdname____ not in birdnames: 
    birdnames.append(birdname____)
  return birdnames

def get_birdnames__mit_brac(birdname):
  birdnames__ = [] 
  birdname_minus_brac_content = re.sub(r'\(.+\)', '', birdname).strip()
  last_term = birdname_minus_brac_content.strip().split(" ")[-1:][0]
  brac_content_terms = re.findall(r'\(.+\)', birdname)[0][1:-1].split("/")
  for term in brac_content_terms: 
    birdnames__.append(term+" "+last_term)
  if birdname_minus_brac_content.find("/")>-1: 
    birdnames___ = return_birdnames__mit_slash(birdname_minus_brac_content) 
    for birdname_ in birdnames___: 
      birdnames__.append(birdname_) 
  else:
    birdnames__.append(birdname_minus_brac_content.strip())
  return birdnames__ 

def get_all_birds_list(wikibirds,ebirds):
  all_birds_list = wikibirds["bird_name"].unique().tolist() #from wikipedia 
  ebird_names = get_ebirds_list(ebirds) 
  for bird in ebird_names: 
    if bird not in all_birds_list:
      all_birds_list.append(bird)
  return all_birds_list 

def get_birdname_words(all_birds_list):
  birdnames_words = []
  for name in all_birds_list: 
    for name_word in name.split(" "):
      name_word = name_word.strip()
      if name_word not in birdnames_words: 
        birdnames_words.append(name_word)
  return birdnames_words
  
#regarding most common spelling mistakes
def get_spelling_corrections():
  spelling_corrections = {}
  spelling_corrections["grey"] = "gray" 
  spelling_corrections["pegion"] = "pigeon" 
  spelling_corrections["brested"] = "breasted" 
  spelling_corrections["serpant"] = "serpent" 
  spelling_corrections["avedavat"] = "avadavat" 
  spelling_corrections["open billed stork"] = "asian openbill" 
  spelling_corrections["secretary bird"] = "Secretarybird" 
  spelling_corrections["dollar bird"] = "dollarbird"
  spelling_corrections["silver bill"] = "silverbill"
  spelling_corrections["eyes"] = "eye" 
  #spelling_corrections["snakebird"] = "anhinga"  
  return spelling_corrections

def replace_emojis(tweet):
  emojis = demoji.findall(tweet) 
  for item in emojis:
    tweet = tweet.replace(item," "+emojis[item]+" ") 
  return tweet

def get_bird_name_from_hashtag_4levels(hashtag_, birdnames): 
  hashtag_ = hashtag_.lower() 
  rel_birdnames = [] 
  for bird in birdnames:
    if bird[-2:] == hashtag_[-2:] and hashtag_[:2] == bird[:2]:
      rel_birdnames.append(bird)
  segments = [0,1,2,3]
  m_ = 2
  while m_<len(hashtag_)-2: 
    segments[0] = hashtag_[:m_] 
    n_ = 0
    while n_<len(hashtag_[m_:]):
      segments[1] = hashtag_[m_:][:n_]
      part3 = hashtag_[m_:][n_:] 
      o_ = 0
      while o_<len(hashtag_[m_:][n_:]): 
        segments[2] = hashtag_[m_:][n_:][:o_] 
        p_ = 0 
        while p_ <len(hashtag_[m_:][n_:][o_:]): 
          segments[3] = hashtag_[m_:][n_:][o_:][:p_]
          part4 = hashtag_[m_:][n_:][o_:][p_:]
          prob_birdname = segments[0] +" " + segments[1] +" " + segments[2] +" " + segments[3] +" " + part4
          prob_birdname = re.sub(r' +', ' ', prob_birdname)  
          if prob_birdname in rel_birdnames: 
            return prob_birdname
          p_ += 1
        o_ += 1 
      n_ += 1
    m_ += 1
  return None 

def try_replacing_hashtags_mit_birdname(text,all_birds_list,birdnames_words):
  status = False  
  hashtags = re.findall(r"#(\w+)", text) 
  for hashtag in hashtags:
    segmented_ = get_bird_name_from_hashtag_4levels(hashtag, all_birds_list)
    if segmented_ is not None: text = text.replace("#"+hashtag,segmented_)
  return text

def basic_preprocess(tweet, spelling_corrections): 
  tweet = tweet.lower()
  tweet = tweet.replace("\n"," ")  
  tweet = tweet.replace("\\n"," ") 
  tweet = p.clean(tweet)  
  if tweet[:2] == "b'": tweet = tweet[1:] 
  tweet = tweet.replace("'","")
  tweet = re.sub(r'[^\w\s]', ' ', tweet)
  tweet = re.sub(r' x..', '', tweet)
  tweet = re.sub(r' +', ' ', tweet)  
  tweet = tweet.strip()
  for key in spelling_corrections: 
    if tweet.find(key)>-1: 
      tweet = tweet.replace(key,spelling_corrections[key])
  return tweet 

def plural_nn_to_singular(tweet, response, birdnames_words):
  try:
    tags = nltk.pos_tag(word_tokenize(tweet))
  except Exception as e:
    response['error'].append("plural_nn_to_singular: Failed to generate tags") 
    response['error'].append(str(e))
  
  is_noun = lambda pos: pos[:2] == 'NN' 
  nouns = [word for (word, pos) in tags if is_noun(pos)]  
  for noun in nouns:
    if noun[-1:] == "s" and noun not in birdnames_words: 
      tweet = tweet.replace(noun, noun[:-1]) 
  return tweet, response

def return_alt_word(word_,birdnames_words): 
  min_distance = 1000
  if word_ not in birdnames_words: 
    for word in birdnames_words: 
      dist_ = levenshtein_distance(word_,word)
      if dist_ < min_distance: 
        min_distance = dist_
        word__ = word 
  else: 
    return word_  
  return word__

def get_bird_names(tweet, birdnames_words, response):
  
  api_url = "https://bird-name-ner-nlp.herokuapp.com/ner?sent="+tweet
  response__ = requests.get(api_url).json() 
  bird_list_= [] 
  
  for bird in response__['bird-wiki']: 
    if bird not in bird_list_: 
      bird_list_.append(bird) 
  for bird in response__['bird-ebird']: 
    if bird not in bird_list_: 
      bird_list_.append(bird) 
      
  response['message'].append("6: [Birds found by rule matching] "+ str(bird_list_))
  
  for bird in response__['bird-ner']:
    status_ = False 
    if bird not in bird_list_: 
      #check for spelling errors.
      for word in bird.split(" "):
        bird = bird.replace(word, return_alt_word(word,birdnames_words)) 
      if len(bird)>0:
        for bird_ in bird_list_:
          if bird_.find(bird) > -1: #if it is found, then no action.  
            status_ = True #found 
            break
        if status_ == False:
          bird_list_.append(bird) 
          response['message'].append("7: [Birds found by custom NER] "+bird)
  
  response['bird_list'] = bird_list_ 
  return response 

def replace_underscores(tweet):
  tweet = tweet.lower()
  tweet = tweet.replace("_"," ")
  return tweet
  
  
def get_bird_names_from_sentence(tweet,all_birds_list,birdnames_words,spelling_corrections,response): 
  try:
    response['message'].append("1: [Original Tweet] "+tweet)
    tweet = replace_emojis(tweet)       #removes emojis
    response['message'].append("2: [Emojis removed] "+tweet)
    
    tweet = replace_underscores(tweet) #removes underscores   #1579145823073406977 #rose_ringed_parakeet 
    response['message'].append("3: [Underscores removed] "+tweet)
    
    tweet = try_replacing_hashtags_mit_birdname(tweet,all_birds_list, birdnames_words)  #finds bird names in hashtags
    response['message'].append("4: [Hashtag replaced] "+tweet)
    tweet = basic_preprocess(tweet, spelling_corrections) #basic preprocessing like lowercases, removal of hashtags etc.
    response['message'].append("5: [Basic preprocessed] "+tweet)
    tweet, response = plural_nn_to_singular(tweet, response, birdnames_words)  #converts plural nouns to singular form.
    response['message'].append("6: [Nouns singulared] "+tweet)
  except Exception as e:
    response['error'].append("2: [ERROR] Failed in PreProcessing phase.")
    response['error'].append(str(e))
  try:
    response = get_bird_names(tweet, birdnames_words, response)
    
    if len(response['bird_list']) == 0: 
      response['message'].append("7: [Bird Selection] No birds found. :3")
  except Exception as e:
    response['error'].append("3: [ERROR] Failed in finding bird names.")
    response['error'].append(str(e))
  # returns response, most probably with some answer. 
  return response


twitter = create_twitter_app_obj() 
wikibirds = load_all_birds_list() 
ebirds = get_eBird_commonNames_data()
all_birds_list = get_all_birds_list(wikibirds,ebirds)
birdnames_words = get_birdname_words(all_birds_list) 
spelling_corrections = get_spelling_corrections()

@app.route('/') 
def hello_world():
  return render_template('index.html') 

@app.route('/sentence')
def getBirds_sent():
  response = {} 
  response['error'] = []
  response['message'] = []
  response['message'].append("0: [Loaded all birds list]")
  
  try:
    sentence = request.args.get('_inpt_sent')
    sentence = sentence.replace("%23","#") 
  except Exception as e:
    return (str(e)) 
  
  response = get_bird_names_from_sentence(sentence,all_birds_list,birdnames_words,spelling_corrections,response) 
  return response 

@app.route('/ner')
def getBirds():
  response = {} 
  response['error'] = []
  response['message'] = []
  response['message'].append("0: [Loaded all birds list]")
  
  ### gets the argument. 
  try:
    tweet_id = request.args.get('tweet_id')
  except Exception as e: 
    response['error'].append("0: [ERROR] Failed to retrieve tweet_id")
    response['error'].append(str(e))
    return response 
  
  ### gets the tweet text 
  try: 
    tweet = twitter.get_status(tweet_id,tweet_mode="extended").full_text
  except Exception as e:
    response['error'].append("1: [ERROR] Failed to retrieve tweet text")
    response['error'].append(str(e))
    return response 
  response = get_bird_names_from_sentence(tweet,all_birds_list,birdnames_words,spelling_corrections,response) 
  return response 
  
  
if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port = port) 
    #app.run()  # If address is in use, may need to terminate other sessions:
               # Runtime > Manage Sessions > Terminate Other Sessions
      

