from flask import Flask, render_template, request, jsonify
from groq import Groq
from gtts import gTTS
import requests
import PyPDF2
import subprocess
import base64
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

with open("key.txt") as f:
    api_key = f.read().strip()

with open("search_key.txt") as f:
    search_key = f.read().strip()

client = Groq(api_key=api_key)

if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        conversation_history = json.load(f)
else:
    conversation_history = []

uploaded_file_text = ""

CURRENT_INFO_KEYWORDS = [
    "current", "latest", "this week",
    "this month", "this year", "news",
    "score", "weather", "price of", "stock", "live"
]

DATE_TIME_KEYWORDS = [
    "today's date", "what is the date", "what's the date",
    "what day is it", "current date", "current time",
    "what time is it", "what's today", "what is today"
]

LANGUAGE_MAP = {
    "in hindi": ("hi", "Respond in Hindi (Devanagari script). "),
    "in kannada": ("kn", "Respond in Kannada script. "),
    "hindi me": ("hi", "Respond in Hindi (Devanagari script). "),
    "kannada me": ("kn", "Respond in Kannada script. "),
}


def get_current_datetime_info():
    now = datetime.now()
    return now.strftime("Today is %A, %B %d, %Y. The current time is %I:%M %p.")


def web_search(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": search_key, "Content-Type": "application/json"}
    payload = {"q": query}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        results = response.json()
        snippets = []
        if "organic" in results:
            for item in results["organic"][:3]:
                snippets.append(item.get("snippet", ""))
        return " ".join(snippets)
    except Exception as e:
        print("Web search failed:", e)
        return ""


def needs_date_time(message):
    msg = message.lower()
    return any(keyword in msg for keyword in DATE_TIME_KEYWORDS)


def needs_web_search(message):
    msg = message.lower()
    return any(keyword in msg for keyword in CURRENT_INFO_KEYWORDS)


def detect_language(message):
    msg = message.lower()
    for phrase, (lang_code, instruction) in LANGUAGE_MAP.items():
        if phrase in msg:
            return lang_code, instruction
    return "en", ""


def deep_research(topic):
    queries = [
        topic,
        topic + " best options",
        topic + " comparison reviews",
        topic + " price"
    ]
    all_results = []
    for q in queries:
        result = web_search(q)
        if result:
            all_results.append(result)

    combined_info = "\n\n".join(all_results)

    research_prompt = ("Based on this research data, write a clear organized "
                        "report with sections and a final recommendation. "
                        "Topic: " + topic + "\n\nResearch data:\n" + combined_info)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": research_prompt}]
    )
    return response.choices[0].message.content


def creator_mode(request_text, content_type):
    prompts = {
        "video_ideas": ("Generate 10 specific, engaging YouTube video ideas for a Free Fire "
                         "gaming channel. Make them catchy and trending-style. Topic context: "),
        "titles": ("Generate 8 click-worthy, SEO-friendly YouTube titles for a Free Fire "
                   "gaming video. Keep them under 60 characters each. Topic context: "),
        "script": ("Write a short engaging YouTube video script outline (intro, main points, "
                   "outro) for a Free Fire gaming video. Topic context: "),
        "thumbnail": ("Describe 5 eye-catching thumbnail concepts (text, imagery, colors) "
                       "for a Free Fire gaming YouTube video. Topic context: "),
        "seo": ("Generate relevant tags, a description, and hashtags optimized for YouTube "
                "search for a Free Fire gaming video. Topic context: "),
    }
    prompt = prompts.get(content_type, prompts["video_ideas"]) + request_text
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def detect_creator_mode(message):
    msg = message.lower()
    if "video idea" in msg or "content idea" in msg:
        return "video_ideas"
    if "title" in msg and ("youtube" in msg or "video" in msg):
        return "titles"
    if "script" in msg:
        return "script"
    if "thumbnail" in msg:
        return "thumbnail"
    if "seo" in msg or "tags" in msg or "hashtag" in msg:
        return "seo"
    return None


def browser_search(query):
    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.google.com/search?q=" + query.replace(" ", "+"))
        time.sleep(15)
        driver.quit()
        return "I've opened a browser and searched for '" + query + "' on Google."
    except Exception as e:
        print("Browser search failed:", e)
        return "Sorry, I had trouble opening the browser for that search."


def youtube_search(query):
    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.youtube.com")
        time.sleep(3)
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        first_video = driver.find_element(By.CSS_SELECTOR, "a#video-title")
        video_title = first_video.get_attribute("title")
        first_video.click()
        return "I searched YouTube for '" + query + "' and opened the top result: " + video_title
    except Exception as e:
        print("YouTube search failed:", e)
        return "Sorry, I had trouble searching YouTube for that."


def check_command(message):
    global uploaded_file_text
    msg = message.lower()

    if needs_date_time(message):
        return get_current_datetime_info()

    if "forget the document" in msg or "clear document" in msg or "forget document" in msg:
        uploaded_file_text = ""
        return "I've cleared the document from memory."

    creator_type = detect_creator_mode(message)
    if creator_type:
        return creator_mode(message, creator_type)

    if "research" in msg and ("deep" in msg or "best" in msg or "compare" in msg):
        topic = msg.replace("research", "").replace("deep", "").strip()
        return deep_research(topic)

    if "youtube" in msg and ("search" in msg or "find" in msg):
        query = (msg.replace("search youtube for", "")
                    .replace("find on youtube", "")
                    .replace("youtube", "").strip())
        return youtube_search(query)

    if "search" in msg and "browser" in msg:
        query = (msg.split("search")[-1]
                    .replace("for", "")
                    .replace("in browser", "")
                    .replace("browser", "").strip())
        return browser_search(query)

    apps = {
        "safari": "Safari", "notes": "Notes", "calculator": "Calculator",
        "calendar": "Calendar", "music": "Music", "mail": "Mail", "terminal": "Terminal"
    }
    if "open" in msg:
        for keyword, app_name in apps.items():
            if keyword in msg:
                subprocess.run(["open", "-a", app_name])
                return "Opening " + app_name + " for you."

    return None


def safe_speak(text, lang_code="en"):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save("static/reply.mp3")
    except Exception as e:
        print("Voice generation failed:", e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    global uploaded_file_text
    try:
        file = request.files["file"]
        file.save("uploaded.pdf")
        reader = PyPDF2.PdfReader("uploaded.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        uploaded_file_text = text[:3000]
        return jsonify({"status": "File uploaded successfully"})
    except Exception as e:
        print("PDF upload failed:", e)
        return jsonify({"status": "Sorry, I had trouble reading that file."})


@app.route("/vision", methods=["POST"])
def vision_response():
    try:
        file = request.files["image"]
        file.save("uploaded_image.jpg")
        with open("uploaded_image.jpg", "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what you see in this image in detail."},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64_image}}
                    ]
                }
            ]
        )
        reply = response.choices[0].message.content
        safe_speak(reply)
        return jsonify({"reply": reply, "audio": "/static/reply.mp3"})
    except Exception as e:
        print("Vision failed:", e)
        reply = "Sorry, I had trouble analyzing that image."
        safe_speak(reply)
        return jsonify({"reply": reply, "audio": "/static/reply.mp3"})


@app.route("/chat", methods=["POST"])
def chat_response():
    try:
        user_message = request.json.get("message")
        lang_code, lang_instruction = detect_language(user_message)

        command_result = check_command(user_message)
        if command_result:
            reply = command_result
            safe_speak(reply, lang_code)
            return jsonify({"reply": reply, "audio": "/static/reply.mp3"})

        context_message = user_message
        lower_msg = user_message.lower()

        if "help me" in lower_msg or "create a plan" in lower_msg or "how do i start" in lower_msg:
            context_message = (lang_instruction +
                                "The user wants help with a goal. Break this down into a clear, "
                                "numbered, actionable step-by-step plan with 5 to 8 steps. "
                                "Be specific and practical. User's goal: " + user_message)

        elif needs_web_search(user_message):
            search_results = web_search(user_message)
            if search_results:
                context_message = (lang_instruction +
                                    "Here is some current information found on the web: "
                                    + search_results + "\n\nUsing this information, "
                                    "answer the user's question: " + user_message)
        elif lang_instruction:
            context_message = lang_instruction + user_message

        if uploaded_file_text:
            context_message = (lang_instruction + "Document content: " + uploaded_file_text
                                + "\n\nQuestion: " + user_message)

        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]

        conversation_history.append({"role": "user", "content": context_message})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation_history
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})

        with open("memory.json", "w") as f:
            json.dump(conversation_history, f)

        safe_speak(reply, lang_code)
        return jsonify({"reply": reply, "audio": "/static/reply.mp3"})
    except Exception as e:
        print("Chat failed:", e)
        reply = "Sorry, something went wrong on my end. Please try again."
        safe_speak(reply)
        return jsonify({"reply": reply, "audio": "/static/reply.mp3"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
