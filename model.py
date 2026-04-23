import spacy
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("es_core_news_sm")
with open("main.json", encoding="utf-8") as f:
    intents = json.load(f)

patterns = []
responses = []

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(pattern)
        responses.append(intent["responses"])

vectorizer = TfidfVectorizer().fit(patterns)
patterns_vec = vectorizer.transform(patterns)

def get_response(message):
    msg_vec = vectorizer.transform([message])
    sim = cosine_similarity(msg_vec, patterns_vec)
    index = sim.argmax()
    score = sim[0][index]
    if score < 0.2:
        return "Lo siento, no entendí eso. ¿Puedes reformularlo?"
    return random.choice(responses[index])