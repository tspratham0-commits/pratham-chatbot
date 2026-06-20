from flask import Flask, render_template, request, jsonify
from groq import Groq
from gtts import gTTS
import requests
import PyPDF2

app = Flask(__name__)

with open("key.txt") as f:
    api_key = f.read().strip()

with open("search_key.txt") as f:
    search_key = f.read().strip()

client = Groq(api_key=api_key)
conversation_history = []
uploaded_file_text = ""

def web_search(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": search_key, "Content-Type": "application/json"}
    payload = {"q": query}
    response = requests.post(url, headers=headers, json=payload)
    results = response.json()
    snippets = []
    if "organic" in results:
        for item in results["organic"][:3]:
            snippets.append(item.get("snippet", ""))
    return " ".join(snippets)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    global uploaded_file_text
    file = request.files["file"]
    file.save("uploaded.pdf")
    reader = PyPDF2.PdfReader("uploaded.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    uploaded_file_text = text[:3000]
    return jsonify({"status": "File uploaded successfully"})

@app.route("/chat", methods=["POST"])
def chat_response():
    user_message = request.json.get("message")
    
    context_message = user_message
    if uploaded_file_text:
        context_message = f"Document content: {uploaded_file_text}\n\nQuestion: {user_message}"
    
    conversation_history.append({"role": "user", "content": context_message})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation_history
    )
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    
    tts = gTTS(text=reply, lang='en', slow=False)
    tts.save("static/reply.mp3")
    return jsonify({"reply": reply, "audio": "/static/reply.mp3"})

if __name__ == "__main__":
    app.run(debug=True)