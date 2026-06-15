from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
from gtts import gTTS
import os

app = Flask(__name__)

with open("key.txt") as f:
    api_key = f.read().strip()

client = Groq(api_key=api_key)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_response():
    user_message = request.json.get("message")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": user_message}]
    )
    reply = response.choices[0].message.content
    tts = gTTS(text=reply, lang='en', slow=False)
    tts.save("static/reply.mp3")
    return jsonify({"reply": reply, "audio": "/static/reply.mp3"})

if __name__ == "__main__":
    app.run(debug=True)