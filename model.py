import json
import random
import string
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar intents
with open("main.json", encoding="utf-8") as f:
    data = json.load(f)

patterns = []
tags = []
responses = {}

# Normalización avanzada
def normalize(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Preparar dataset
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(normalize(pattern))
        tags.append(intent["tag"])
    responses[intent["tag"]] = intent["responses"]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(patterns)

def predict_intent(message):
    msg = normalize(message)
    vec = vectorizer.transform([msg])
    similarity = cosine_similarity(vec, X)

    index = similarity.argmax()
    score = similarity[0][index]

    if score < 0.35:
        return "unknown"

    return tags[index]

def get_response(message, context):
    intent = predict_intent(message)

    # 🧠 Flujo conversacional
    if context.get("flow") == "pedido":
        if "numero" not in context:
            context["numero"] = message
            return f"Gracias 🙌 Estoy revisando el pedido #{message}...\nTu pedido llegará en 2 días 📦"

    if intent == "problema_pedido":
        context["flow"] = "pedido"
        return "Entiendo 📦 ¿Me proporcionas tu número de pedido?"

    if intent == "ayuda":
        context["flow"] = "soporte"

    if intent == "unknown":
        return random.choice([
            "No entendí bien 🤔 ¿puedes explicarlo diferente?",
            "Hmm... no estoy seguro de eso 😅",
            "¿Puedes darme más detalles?"
        ])

    return random.choice(responses[intent])