# 🧠 MindMirror AI

**Decode your mind. Discover your patterns.**

MindMirror AI is a personal behavioral analyst powered by Google Gemini.
It combines local sentiment analysis with AI-powered deep pattern
recognition to help you understand yourself — your cycles, triggers,
habits, and growth.

---

## ✨ Features

- **📝 Journal** — Write daily entries, batch import, auto-tagging
- **🔬 Analysis** — Local pattern detection + AI deep analysis
- **💬 AI Chat** — Warm therapeutic conversations across multiple sessions
- **📊 Dashboard** — Mood timelines, emotion charts, streaks, word clouds
- **📂 History** — All analyses and chats saved permanently
- **📤 Export** — Download your data as JSON or TXT
- **🎨 7 Themes** — Deep Ocean, Sakura, Forest, Cosmic Purple, Sunrise, Midnight, Clean Light

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/-mindmirror-ai.git
cd -mindmirror-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key

Create the file `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "AIzaSy-your-key-here"
```

Get a free key at: https://aistudio.google.com/app/apikey

### 4. Run the app

```bash
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the main file
4. Go to **Settings → Secrets** and paste:

```toml
GEMINI_API_KEY = "AIzaSy-your-key-here"
```

5. Click **Deploy**

> ⚠️ Do NOT commit your `.streamlit/secrets.toml` to GitHub.
> Add it to `.gitignore`.

---

## 📁 File Structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app (UI, routing, pages) |
| `analyzer.py` | Sentiment analysis, Gemini AI calls |
| `database.py` | SQLite persistence layer |
| `themes.py` | 7 visual themes with CSS + Plotly colors |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml` | API key (local only, do not commit) |

---

## 🔒 Privacy

- All journal data is stored locally in SQLite (`mindmirror.db`)
- Journal text is only sent to Google Gemini when you explicitly:
  - Run **AI Deep Analysis**
  - Use **AI Chat**
- No data is shared with third parties beyond Gemini API calls

---

## 📝 License

MIT License — use freely, modify freely, share freely.
