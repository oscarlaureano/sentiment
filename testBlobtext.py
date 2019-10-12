from textblob import TextBlob

count = 0
positive = 0
neutral = 0
negative = 0

with open("frases.txt","r") as f:
    for line in f.read().split('\n'):
        analysis = TextBlob(line)
        try:
            eng=analysis.translate(to='en')
            if eng.sentiment.polarity > 0:
                print("___Positiva___",eng.sentiment)
                positive += 1
                print(line)
                print(eng)
            elif eng.sentiment.polarity == 0:
                print("___Neutral___",eng.sentiment)
                neutral += 1
                print(line)
                print(eng)
            elif eng.sentiment.polarity < 0:
                print("___Negativa___",eng.sentiment)
                negative += 1
                print(line)
                print(eng)
            count +=1
        except:
            #Mostramos este mensaje en caso de que se presente algún problema
            print ("El elemento no está presente")


print("Precisión positiva = {}% via {}/{} ejemplos".format(positive/count*100.0,positive, count))
print("Precisión neutral = {}% via {}/{} ejemplos".format(neutral/count*100.0,neutral, count))
print("Precisión negativa = {}% via {}/{} ejemplos".format(negative/count*100.0,negative, count))

#print(analysis.sentiment)

#print(analysis.tags)

#print(analysis.translate(to='es'))

#print(dir(analysis)
