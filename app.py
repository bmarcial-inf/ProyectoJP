from flask import Flask, render_template, request, jsonify, session
from model import get_response

app = Flask(__name__)
app.secret_key = "chatbot_secret"

@app.route("/")
def home():
    if "chat" not in session:
        session["chat"] = []
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    msg = request.json["message"]
    response = get_response(msg)

    chat = session.get("chat", [])
    chat.append({"user": msg, "bot": response})
    session["chat"] = chat

    return jsonify({"response": response, "chat": chat})

@app.route("/clear")
def clear():
    session["chat"] = []
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)