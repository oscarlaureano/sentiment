from flask import Flask, render_template, request 
from textblob import TextBlob
import tweepy as tw

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    phrase = request.form['phrase']

    search_words = phrase

    tweets = tw.Cursor(api.search,
              q=search_words,
              lang="es",
              result_type="recent").items(5)
    
    user_name = []
    followers = []
    tweet_text = []
    user_loc = []
    retweets = []
    favs = []
    tweet_url = []
    
    for tweet in tweets:
        user_name.append(tweet.user.screen_name)
        followers.append(tweet.user.followers_count)
        tweet_text.append(tweet.text)
        user_loc.append(tweet.coordinates)
        retweets.append(tweet.retweet_count)
        favs.append(tweet.favorite_count)
        tweet_url.append("https://twitter.com/"+str(tweet.user.screen_name)+"/status/"+str(tweet.id))

    tweets_info = [user_name, followers, tweet_text, user_loc, retweets, favs, tweet_url]
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