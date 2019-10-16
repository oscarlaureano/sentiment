from flask import Flask, render_template, request 
from textblob import TextBlob
import tweepy as tw
import pandas as pd

# API keys
consumer_key = 'Ld7ked0EiVaLheisfgQTRGje0'
consumer_secret = 'qU0NibfLnadfarQ173zGUJQaJiWjeUy3FuTrTp7mFqCYvTYIqk'
access_token = '324115646-LFpGzemboLymy8jR6qllikAdsrrLOa5RrUcouFMS'
access_token_secret = 'vq7TZJVWDxgjEq48gt0NC8JRduYuwwSinfbUObgPinjCY'

# Authentication for the Twitter API
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    # Word or words to search
    phrase = request.form['phrase']

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
    user_loc = []
    retweets = []
    favs = []
    tweet_url = []
    sentiment = []
    
    # Getting the relevant information from the list of Tweet objects
    for tweet in tweets:
        numRows += 1
        ids.append(numRows)
        user_name.append(tweet.user.screen_name)
        followers.append(tweet.user.followers_count)
        tweet_text.append(tweet.text)
        user_loc.append(tweet.place)
        retweets.append(tweet.retweet_count)
        favs.append(tweet.favorite_count)
        tweet_url.append("https://twitter.com/"+str(tweet.user.screen_name)+"/status/"+str(tweet.id))
        sentiment.append('None yet')
    
    # Creating a dictionary with lists 
    dictTweets = {'id':ids, 'username': user_name, 'followers': followers, 'text': tweet_text, 'location': user_loc, 'retweets': retweets, 'favs': favorite_count, 'link': tweet_url, 'sentiment': sentiment}
    # Using the dictionary to create a dataFrame for plotting
    dfTweets = pd.DataFrame(dictTweets)

    # Merging info into a list
    tweets_info = [user_name, followers, tweet_text, user_loc, retweets, favs, tweet_url]
    # Showing the results on front-end
    return render_template("index.html", info = tweets_info)

    

    # Analysis code
    # analysis = TextBlob(phrase)
    # try:
    #     eng=analysis.translate(to='en')
    #     if eng.sentiment.polarity > 0:
    #         salida = "___Positiva___:"+str(eng.sentiment)
    #         return render_template("index.html", result=salida)
    #     elif eng.sentiment.polarity == 0:
    #         salida = "___Neutral___:"+str(eng.sentiment)
    #         return render_template("index.html", result=salida)
    #     elif eng.sentiment.polarity < 0:
    #         salida = "Negativa: "+str(eng.sentiment)
    #         return render_template("index.html", result=salida, original=phrase, translated=eng)
    # except:
    #     print ("El elemento no está presente")
    #     salida = "El elemento no está presente"
    #     return render_template("index.html", result=salida)


if __name__ == "__main__":
    app.run(debug=True)