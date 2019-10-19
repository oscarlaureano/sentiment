# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import tweepy as tw
import pandas as pd
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from words import positiveWords, negativeWords, stopWords
import plotly.graph_objects as go
import re
import collections
import random

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
numMaxRows = 5
bagOfWords = dict()
listBag = []
listWords = []



def getSentiment(line):
    global bagOfWords
    global listWords

    analysis = TextBlob(line, analyzer=NaiveBayesAnalyzer())
    sentiment = 0

    line = line.lower()
    line = re.sub(r'[^a-z\s]','',line)

    words = line.split()
    words = [word for word in words if word not in stopWords]

    listWords.extend(words)

    for word in words:
        if word in positiveWords:
            sentiment += 0.1
        elif word in negativeWords:
            sentiment -= 0.15
        
        if word in bagOfWords:
            bagOfWords[word] += 1
        else:
            bagOfWords[word] = 1
    
    try:
        eng=analysis.translate(to='en')
        sentiment += eng.sentiment.polarity
        
        return sentiment
    except:
        return sentiment

def getTweets(phrase, numOfTweets):
    global dfTweets

    # Query to twitter
    tweets = tw.Cursor(api.search,
              q=phrase,
              lang="es",
              result_type="recent").items(numOfTweets)
    
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
    feeling = []
    
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
        sentiment.append(getSentiment(tweet.text))
        if sentiment[numRows-1] < 0:
            feeling.append('negativo')
        elif sentiment[numRows-1] == 0:
            feeling.append('neutral')
        else:
            feeling.append('positivo')
    
    # Creating a dictionary with lists 
    dictTweets = {'id':ids, 'username': user_name, 'followers': followers, 'text': tweet_text, 'retweets': retweets, 'favs': favs, 'link': tweet_url, 'date': tweet_date, 'sentiment': sentiment, 'feeling': feeling}
    # Using the dictionary to create a dataFrame for plotting
    dfTweets = pd.DataFrame(dictTweets)
    #dfTweets.to_csv(r'C:/Users/oscar/Desktop/tweets.csv')

# ---------------------------------------------------------------------------------------
# --------------------------- /Getting Data ---------------------------------------------
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# --------------------------- Generating Graphs -----------------------------------------
# ---------------------------------------------------------------------------------------

def generate_Table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def generate_Bag():
    global listBag
    listBag = list(bagOfWords.items())
    return html.Ul([html.Li(x) for x in listBag])

def generate_Interacciones(type):
    title = 'Interacciones en Twitter'
    y = [0,0,0]
    x = ['Followers', 'Retweets', 'Favs']
    if type == 'empty':
        return {
            'data': [
                {'x': x, 'y': y, 'type': 'bar'}
            ],
            'layout': {
                'title': title
            }
        }
    else:
        y = [dfTweets['followers'].sum(),dfTweets['retweets'].sum(),dfTweets['favs'].sum()]
        return {
            'data': [
                {'x': x, 'y': y, 'type': 'bar'}
            ],
            'layout': {
                'title': title
            }
        }

def generate_Sentimiento(type):
    global dfTweets

    title = 'Analisis de Sentimientos'
    colors = ['lightgreen','lightblue','lightcoral']
    values = [33,33,34]
    labels = ['Positivos', 'Neutrales', 'Negativos']
    
    if type == 'empty':
        return {
            'data': [{
                'values': values, 
                "labels": labels, 
                'type': 'pie', 
                'hole': '0.4', 
                'marker': {
                    'colors': colors
                    }
                }], 
            'layout': {'title': title}
        }
    else: 
        df = dfTweets[['sentiment','feeling']]
        data = df.groupby(df['feeling']).count().reset_index()

        values = list(data['sentiment'])
        labels = list(data['feeling'])

        try:
            pos = labels.index('positivo')
            colors[pos] = 'lightgreen'
        except:
            colors = colors
        try:
            pos = labels.index('neutral')
            colors[pos] = 'lightblue'
        except:
            colors = colors
        try:
            pos = labels.index('negativo')
            colors[pos] = 'lightcoral'
        except:
            colors = colors

        return {
            'data': [{
                'values': values, 
                'labels': labels, 
                'type': 'pie',
                'hole': '0.4',
                'marker': {
                'colors': colors
                    }
                }], 
            'layout': {
                'title': title
                }
            }

def generate_Cloud():
    global listWords

    counter=collections.Counter(listWords)

    wordmap = pd.DataFrame(list(counter.items()), columns=['Words', 'Count'])

    words = dir(go)[:30]

    weights = list(wordmap['Count'])

    data = go.Scatter(x=[random.random() for i in range(30)],
                    y=[random.random() for i in range(30)],
                    mode='text',
                    text= list(wordmap['Words']),
                    marker={'opacity': 0.3},
                    textfont={'size': [i*10 for i in weights]})
    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})
    
    return {'data': [data], 'layout': layout}

# ---------------------------------------------------------------------------------------
# --------------------------- /Generating Graphs -----------------------------------------
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# --------------------------- Dash App --------------------------------------------------
# ---------------------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#EEEEEE',
    'text': '#7FDBFF',
    'non-important-text': '#66AFCC',
    'gray' : '#406D80',
    'blue' : '#66AFCC',
    'darkblue' : '#26424D'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Posición de marca en redes sociales',
        style={
            'color': colors['darkblue']
        }
    ),

    html.Div(children='''Busca alguna frase o palabras''',
        style={
            'color': colors['non-important-text']
        }
    ),
    
    html.Div(children=[
        dcc.Input(id='input-phrase', type='text', style={'float': 'left'}),
        daq.NumericInput(id='my-numeric-input', value=5, style={'float': 'left'}),
        html.Button(id='submit-button', n_clicks=0, children='Buscar',
            style={
                'color': colors['gray'],
                'float': 'left'
            })
        ]
    ),

    html.Div(id='output-state',
        style={
            'color': colors['non-important-text'],
            'clear': 'left'
        }
    ),
    html.Div(children=[
        dcc.Graph(
            id='interacciones',
            figure={}
        )],
        style={
            'float': 'left',
            'width': '60%'
            }
    ),
    html.Div(children=[
        dcc.Graph(
            id='sentimientos',
            figure={}
        )],
        style={
            'float': 'left',
            'width': '40%'
        }
    ),
    dcc.Graph(
        id='cloud',
        figure={},
        style={
            'clear': 'left'
        }
    ),
    html.Table(id='dataframe-table',
        style={
            'color': colors['blue'],
            'backgroundColor': '#DDDDDD',

        }
    ),

    
])
# ---------------------------------------------------------------------------------------
# --------------------------- /Dash App --------------------------------------------------
# ---------------------------------------------------------------------------------------
@app.callback([Output('output-state', 'children'),
              Output('dataframe-table', 'children'),
              Output('interacciones','figure'),
              Output('sentimientos', 'figure'),
              Output('cloud','figure')],
              [Input('submit-button', 'n_clicks')],
              [State('input-phrase', 'value'),
              State('my-numeric-input', 'value')])


def update_output(nclicks, phrase, numOfTweets):
    global dfTweets
    global listWords

    listWords = []
    
    max_rows = numMaxRows
    emptyInteracciones = generate_Interacciones('empty')
    emptySentimientos = generate_Sentimiento('empty')
    if phrase != None:
        getTweets(phrase,numOfTweets)
        outputState = u'''Resultados para la búsqueda de: {}'''.format(phrase)
        dataframeTable = generate_Table(dfTweets, max_rows)
        interacciones = generate_Interacciones('filled')
        sentimientos = generate_Sentimiento('filled')
        return outputState, dataframeTable, interacciones, sentimientos, generate_Cloud()
    
    return "",[],emptyInteracciones, emptySentimientos, {}

if __name__ == '__main__':
    app.run_server(debug=True)