from flask import Flask, render_template, request, jsonify, session
from model import get_response

app = Flask(__name__)
app.secret_key = "ultra_secret"

@app.route("/")
def home():
    session.setdefault("chat", [])
    session.setdefault("context", {})
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    msg = request.json.get("message")
    context = session.get("context", {})

    response = get_response(msg, context)

    session["chat"].append({"user": msg, "bot": response})
    session["context"] = context

    return jsonify({
        "response": response
    })

@app.route("/clear")
def clear():
    session.clear()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)