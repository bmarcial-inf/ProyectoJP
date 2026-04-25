from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from model import get_response
import os
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret_key")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
@app.route("/")
def home():
    session.setdefault("chat", [])
    session.setdefault("context", {})
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    msg = request.json["message"]
    context = session.get("context", {})
    response = get_response(msg, context)
    log = {
        "mensaje": msg,
        "respuesta": response,
        "hora": str(datetime.now())
    }
    with open("logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    chat_historial = session.get("chat", [])
    chat_historial.append({
        "user": msg,
        "bot": response
    })
    session["chat"] = chat_historial
    session["context"] = context
    return jsonify({
        "response": response
    })

@app.route("/clear")
def clear():
    session.clear()
    return jsonify({
        "status": "ok"
    })
if __name__ == "__main__":
    app.run(debug=True)