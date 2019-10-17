# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import tweepy as tw
import pandas as pd

# ---------------------------------------------------------------------------------------
# --------------------------- Getting Data ----------------------------------------------
# ---------------------------------------------------------------------------------------
# API keys
consumer_key = 'z45P1zec5Hf1a3fHRCFRQZ8hb'
consumer_secret = '3NluFyOOCuIT5mdCqHvNfk0Z4tgWMW26nwKS2XlPFg1RBBakAH'
access_token = '324115646-LFpGzemboLymy8jR6qllikAdsrrLOa5RrUcouFMS'
access_token_secret = 'vq7TZJVWDxgjEq48gt0NC8JRduYuwwSinfbUObgPinjCY'

# Authentication for the Twitter API
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


dfTweets = pd.DataFrame()

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def getTweets(phrase):
    global dfTweets

    # Query to twitter
    tweets = tw.Cursor(api.search,
              q=phrase,
              lang="es",
              result_type="recent").items(5)
    
    # Lists for retrieving info
    numRows = 0
    ids = []
    user_name = []
    followers = []
    tweet_text = []
    retweets = []
    favs = []
    tweet_url = []
    tweet_date = []
    sentiment = []
    
    # Getting the relevant information from the list of Tweet objects
    for tweet in tweets:
        numRows += 1
        ids.append(numRows)
        user_name.append('@'+str(tweet.user.screen_name))
        followers.append(tweet.user.followers_count)
        tweet_text.append(tweet.text)
        retweets.append(tweet.retweet_count)
        favs.append(tweet.favorite_count)
        tweet_url.append("https://twitter.com/"+str(tweet.user.screen_name)+"/status/"+str(tweet.id))
        tweet_date.append(tweet.created_at)
        sentiment.append('None yet')
    
    # Creating a dictionary with lists 
    dictTweets = {'id':ids, 'username': user_name, 'followers': followers, 'text': tweet_text, 'retweets': retweets, 'favs': favs, 'link': tweet_url, 'date': tweet_date, 'sentiment': sentiment}
    # Using the dictionary to create a dataFrame for plotting
    dfTweets = pd.DataFrame(dictTweets)
    
# ---------------------------------------------------------------------------------------
# --------------------------- /Getting Data ----------------------------------------------
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# --------------------------- Dash App --------------------------------------------------
# ---------------------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Posición de marca en redes sociales'),

    html.Div(children='''Busca alguna frase o palabras'''),
    
    dcc.Input(id='input-phrase', type='text'),
    html.Button(id='submit-button', n_clicks=0, children='Buscar'),
    html.Div(id='output-state'),

    html.Table(id='dataframe-table')
])
# ---------------------------------------------------------------------------------------
# --------------------------- /Dash App --------------------------------------------------
# ---------------------------------------------------------------------------------------
@app.callback([Output('output-state', 'children'),
              Output('dataframe-table', 'children')],
              [Input('submit-button', 'n_clicks')],
              [State('input-phrase', 'value')])

def update_output(nclicks, input1):
    global dfTweets
    max_rows = 5
    if input1 != None:
        getTweets(input1)
        return u'''Resultados para la búsqueda de: {}'''.format(input1), generate_table(dfTweets, max_rows)
    return "",[]

if __name__ == '__main__':
    app.run_server(debug=True)