# model.py

import json
import random
import string
import unicodedata
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open("main.json", encoding="utf-8") as f:
    data = json.load(f)

patterns = []
tags = []
responses = {}

def normalize(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text.translate(str.maketrans('', '', string.punctuation))

for intent in data["intents"]:
    for p in intent["patterns"]:
        patterns.append(normalize(p))
        tags.append(intent["tag"])
    responses[intent["tag"]] = intent["responses"]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(patterns)

pedidos_db = {
    "123": {"estado": "En camino", "dias": 2},
    "456": {"estado": "Entregado", "dias": 0},
    "789": {"estado": "Retrasado", "dias": 5}
}

def predict_intent(message):
    msg = normalize(message)
    vec = vectorizer.transform([msg])
    sim = cosine_similarity(vec, X)
    i = sim.argmax()

    if sim[0][i] < 0.35:
        return "unknown"

    return tags[i]

def get_response(message, context):
    msg = message.lower()
    intent = predict_intent(message)

    hora = datetime.now().hour

    if hora < 12:
        saludo_tiempo = "Buenos días ☀️"
    elif hora < 18:
        saludo_tiempo = "Buenas tardes 🌤️"
    else:
        saludo_tiempo = "Buenas noches 🌙"

    nombre = context.get("nombre", "")
    prefijo = f"{nombre}, " if nombre else ""

    # Guardar nombre
    if "mi nombre es" in msg:
        name = message.split("es")[-1].strip()
        context["nombre"] = name
        return f"Mucho gusto {name} 😊|menu"

    # Emociones
    if any(x in msg for x in ["enojado", "molesto", "mal servicio"]):
        return "Lamento la situación 😔 voy a ayudarte enseguida."

    # Humano
    if "hablar con humano" in msg:
        return "Te conectaré con un agente 👨‍💼"

    # Flujo pedido
    if context.get("flow") == "pedido":

        if not message.isdigit():
            return "El número de pedido debe ser numérico 🔢"

        data = pedidos_db.get(message)

        if not data:
            return "📦 Pedido no encontrado"

        context["flow"] = None

        return f"""📦 Pedido {message}
Estado: {data['estado']}
Entrega estimada: {data['dias']} días|menu"""

    if intent == "problema_pedido":
        context["flow"] = "pedido"
        return "📦 ¿Cuál es tu número de pedido?"

    # Ayuda
    if intent == "ayuda":
        return "Claro 👍 ¿Qué necesitas?|menu"

    # No entendido
    if intent == "unknown":
        context["fails"] = context.get("fails", 0) + 1

        if context["fails"] >= 3:
            return "No logro entenderte bien. Te conectaré con un agente 👨‍💼"

        return "No entendí bien 🤔 ¿Es sobre pedido, horarios o contacto?|menu"

    context["fails"] = 0

    respuesta = random.choice(responses[intent])

    # Menú en saludos / gracias
    if intent in ["saludo", "gracias"]:
        return f"{saludo_tiempo} {prefijo}{respuesta}|menu"

    return f"{saludo_tiempo} {prefijo}{respuesta}"