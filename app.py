from flask import Flask, render_template, request, jsonify, session
from model import get_response
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"

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
        f.write(json.dumps(log) + "\n")

    session["chat"].append({"user": msg, "bot": response})
    session["context"] = context

    return jsonify({"response": response})

@app.route("/clear")
def clear():
    session.clear()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)