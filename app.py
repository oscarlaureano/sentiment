from flask import Flask, render_template, request 
from textblob import TextBlob

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    phrase = request.form['phrase']

    print(phrase)

    # Analysis code
    analysis = TextBlob(phrase)
    try:
        eng=analysis.translate(to='en')
        if eng.sentiment.polarity > 0:
            salida = "___Positiva___:"+str(eng.sentiment)
            return render_template("index.html", result=salida)
        elif eng.sentiment.polarity == 0:
            salida = "___Neutral___:"+str(eng.sentiment)
            return render_template("index.html", result=salida)
        elif eng.sentiment.polarity < 0:
            salida = "Negativa: "+str(eng.sentiment)
            return render_template("index.html", result=salida, original=phrase, translated=eng)
    except:
        print ("El elemento no está presente")
        salida = "El elemento no está presente"
        return render_template("index.html", result=salida)


if __name__ == "__main__":
    app.run(debug=True)