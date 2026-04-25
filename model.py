import json
import random
import string
import unicodedata
import os
import pymysql

from dotenv import load_dotenv
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
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
    return text.translate(
        str.maketrans('', '', string.punctuation)
    )
for intent in data["intents"]:
    for p in intent["patterns"]:
        patterns.append(normalize(p))
        tags.append(intent["tag"])
    responses[intent["tag"]] = intent["responses"]
vectorizer = TfidfVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(patterns)

def buscar_pedido(numero):
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        sql = """
        SELECT estado, dias, ubicacion
        FROM pedidos
        WHERE id = %s
        """
        cursor.execute(sql, (int(numero),))
        data = cursor.fetchone()
        print("BUSCANDO:", numero)
        print("RESULTADO:", data)
        conn.close()
        return data
    except Exception as e:
        print("ERROR MYSQL:", e)
        return None

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
    if "mi nombre es" in msg:
        name = message.split("es")[-1].strip()
        context["nombre"] = name
        return f"Mucho gusto {name} 😊|menu"
    if any(x in msg for x in ["enojado", "molesto", "mal servicio"]):
        return "Lamento la situación 😔 voy a ayudarte enseguida."
    if "hablar con humano" in msg:
        return "Te conectaré con un agente 👨‍💼"
    if context.get("flow") == "pedido":
        if not message.isdigit():
            return "El número de pedido debe ser numérico 🔢"
        pedido = buscar_pedido(message)
        if not pedido:
            return "📦 Pedido no encontrado"
        estado, dias, ubicacion = pedido
        context["flow"] = None
        return f"""📦 Pedido {message}
Estado: {estado}
Ubicación: {ubicacion}
Entrega estimada: {dias} días|menu"""
    if intent == "problema_pedido":
        context["flow"] = "pedido"
        return "📦 ¿Cuál es tu número de pedido?"
    if intent == "ayuda":
        return "Claro 👍 ¿Qué necesitas?|menu"
    if intent == "unknown":
        context["fails"] = context.get("fails", 0) + 1
        if context["fails"] >= 3:
            return "No logro entenderte bien. Te conectaré con un agente 👨‍💼"
        return "No entendí bien 🤔 ¿Es sobre pedido, horarios o contacto?|menu"
    context["fails"] = 0
    respuesta = random.choice(
        responses.get(intent, ["No entendí"])
    )
    if intent in ["saludo", "gracias"]:
        return f"{saludo_tiempo} {prefijo}{respuesta}|menu"
    return f"{saludo_tiempo} {prefijo}{respuesta}"
