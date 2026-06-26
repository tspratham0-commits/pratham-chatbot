# NOVA — Personal AI Assistant

NOVA is a personal AI assistant built from scratch using Python, Flask, and the Groq API. It can talk, remember things, search the web, read documents, see images, control your computer, automate browsers, and track your goals and projects over time.

Built by [Pratham](https://github.com/tspratham0-commits) — a self-taught 19-year-old developer from Haveri, Karnataka, India.

## Features

- **Voice replies** — NOVA speaks its answers out loud (multi-language support included — try adding "in hindi" or "in kannada" to any message)
- **Long-term memory** — remembers your conversation across server restarts
- **Project Memory System** — tracks your actual goals and projects with status and progress notes (e.g. "my goal is to launch a YouTube channel")
- **Smart web search** — automatically searches the web for current/time-sensitive questions
- **Deep Research Mode** — combines multiple searches into one organized report (try: "do deep research on best gaming phones under 20000")
- **PDF reading** — upload a PDF and ask questions about it
- **Vision** — upload an image and NOVA describes what it sees
- **Computer control** — say "open calculator" / "open safari" / "open notes" etc.
- **Browser automation** — searches Google or YouTube and opens results for you
- **Multi-step planning** — ask "help me launch a gaming channel" for a full action plan
- **Creator Mode** — generates YouTube video ideas, titles, scripts, thumbnail concepts, and SEO tags
- **Specialist Agents** — automatically switches expert "personas" for coding, gaming/content creation, or career questions
- **Self-Correction** — checks its own answers before sending them, and retries if the answer doesn't address the question
- **AI-powered tool routing** — figures out your intent even with imperfect phrasing

## Setup

### 1. Requirements
- Python 3.9+
- Google Chrome (for browser automation features)
- A free [Groq API key](https://console.groq.com)
- A free [Serper API key](https://serper.dev) for web search

### 2. Install dependencies
```bash
pip3 install flask groq gtts requests PyPDF2 selenium webdriver-manager
```

### 3. Add your API keys
Create two files in the project folder (these are git-ignored and never committed):

**key.txt** — paste only your Groq API key, nothing else
```
your_groq_api_key_here
```

**search_key.txt** — paste only your Serper API key, nothing else
```
your_serper_api_key_here
```

### 4. Run it
```bash
python3 app.py
```

Then open your browser to:
```
http://127.0.0.1:5001
```

### 5. Access from your phone (optional)
Make sure your phone is on the same WiFi as your computer, then visit:
```
http://YOUR_COMPUTER_IP:5001
```
(Find your IP with `ipconfig getifaddr en0` on Mac)

## How to use it

Click any of the quick-action buttons in the interface, or just type naturally:

| Try saying | What happens |
|---|---|
| "my goal is to launch a [project]" | Creates a tracked project |
| "what are my projects" | Shows everything being tracked |
| "do deep research on [topic]" | Multi-source research report |
| "give me video ideas for [topic]" | Creator Mode content ideas |
| "open calculator" | Opens an app on your computer |
| "search youtube for [topic]" | Opens YouTube and plays top result |
| "help me [goal]" | Step-by-step action plan |
| "forget the document" | Clears any uploaded PDF |
| Add "in hindi" or "in kannada" | Replies in that language |

## Project structure
```
.
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Web interface
├── static/
│   └── reply.mp3        # Generated voice replies (auto-created)
├── key.txt              # Your Groq API key (not committed)
├── search_key.txt        # Your Serper API key (not committed)
├── memory.json           # Conversation memory (not committed)
├── projects.json          # Project tracking data (not committed)
└── .gitignore
```

## Known limitations

- General "what's the latest news today" queries (without a specific topic) don't work well — the underlying search API needs something specific to search for
- Browser automation can occasionally trigger CAPTCHA verification from Google
- Browser windows stay open until manually closed (by design, so you can read results)
- This is a personal project built for learning, not a production-hardened service

## Built with
Python · Flask · Groq API (Llama models) · Google Text-to-Speech (gTTS) · Selenium · Serper Search API

---

*This project was built iteratively over several sessions, debugging real issues along the way — deprecated model names, API quota limits, indentation errors, security leaks from exposed API keys, and reliability improvements. Every feature here is genuinely working and tested.*
