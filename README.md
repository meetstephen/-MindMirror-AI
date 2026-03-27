[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)](#)

# 🧠 MindMirror AI v2.0

**AI-powered personal behavioral analyst and journaling companion.**

MindMirror AI combines local sentiment analysis with Google Gemini-powered deep pattern recognition to help you decode your emotional cycles, cognitive patterns, behavioral triggers, and personal growth — in a Streamlit-powered deployment built for **self-discovery and mental wellness**.

<p align="center">
  <a href="https://mindmirror-ai.streamlit.app">
    <img src="https://img.shields.io/badge/🚀%20Launch%20App-MindMirror%20AI%20Live-059669?style=for-the-badge&logoColor=white" alt="Launch MindMirror AI">
  </a>
</p>

<p align="center">
  👉 <strong><a href="https://mindmirror-ai.streamlit.app">https://mindmirror-ai.streamlit.app</a></strong>
</p>

---

## Features

- **AI Journal** — write daily entries, batch import past notes, auto-tagging, and sentiment scoring on every save
- **Local Pattern Analysis** — emotion detection, topic extraction, word frequency, entity recognition, and sentiment timelines without any API calls
- **AI Deep Analysis** — Gemini-powered behavioral report with cognitive patterns, emotional loops, triggers, predictions, and personalised recommendations (up to 8,192 tokens)
- **AI Insight Chat** — warm therapeutic conversations with multi-turn memory, journal context awareness, and multiple saved sessions (up to 4,096 tokens per reply)
- **Preset Chat Sessions** — Morning Check-in, Evening Reflection, Deep Dive, Goal Setting, Mood Check, plus custom-named sessions
- **Insight Dashboard** — mood timelines, emotion distribution, topic breakdown, word frequency charts, people mentions, journaling streaks, and mood calendar heatmap
- **AI Reflection Prompts** — personalised journaling prompts generated from your recent entries
- **SQLite Persistence** — journal entries, analyses, chat history, and user profiles survive browser refreshes, app restarts, and redeployments
- **Auto-login** — username persists in URL parameters so refreshing never loses your session
- **Export** — download journal entries and analyses as JSON or TXT
- **7 Themes** — Deep Ocean · Sakura · Forest · Cosmic Purple · Sunrise · Midnight · Clean Light

## Navigation

The app is organised into 6 top-level pages:

| Page | Purpose |
|---|---|
| 📝 Journal | Write entries, batch import, browse and delete past entries |
| 🔬 Analysis | Local pattern detection + AI deep behavioral analysis |
| 💬 AI Chat | Therapeutic conversations with session management |
| 📊 Dashboard | Mood timelines, emotion charts, streaks, word clouds, mood calendar |
| 📂 History | Browse saved analyses, chat transcripts, and export data |
| ⚙️ Settings | API key status, account stats, theme info, danger zone |

## AI Models

| Model | ID |
|---|---|
| Gemini 2.5 Flash | `gemini-2.5-flash` |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` |
| Gemini 2.0 Flash | `gemini-2.0-flash` |
| Gemini 2.0 Flash Lite | `gemini-2.0-flash-lite` |
| Gemini 1.5 Flash | `gemini-1.5-flash` |
| Gemini 1.5 Pro | `gemini-1.5-pro` |

Models are selectable from the sidebar. Default is `gemini-2.5-flash`.

## Quick Start

### Try it now

Visit **[mindmirror-ai.streamlit.app](https://mindmirror-ai.streamlit.app)** — no installation needed.

### Run locally

```bash
# Clone
git clone https://github.com/meetstephen/-MindMirror-AI.git
cd -MindMirror-AI

# Install dependencies
pip install -r requirements.txt

# Configure API key
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
GEMINI_API_KEY = "your-api-key-here"
EOF

# Run
streamlit run app.py
```

Alternatively, get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey) and set it in the Streamlit Cloud Secrets dashboard.

## Configuration

All options go in `.streamlit/secrets.toml`:

| Key | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |

### Example

```toml
GEMINI_API_KEY = "AIzaSy-your-key-here"
```

## Analysis Modes

| Mode | Description | Token Limit |
|---|---|---|
| 📊 Local Analysis | Sentiment, emotions, topics, entities, word frequency — no API needed | Instant |
| 🤖 AI Deep Analysis | Full behavioral report with patterns, predictions, triggers, and recommendations | 8,192 |

## AI Capabilities

| Capability | Description |
|---|---|
| 🔍 Pattern Detection | Recurring emotional and behavioral cycles |
| 🧠 Cognitive Analysis | All-or-nothing thinking, catastrophising, filtering, emotional reasoning |
| ⏳ Predictions | Pattern-based forecasting of emotional trajectories |
| ⚠️ Trigger Mapping | Specific triggers linked to emotional effects |
| 💬 Therapeutic Chat | Warm, validating conversations with gentle pattern surfacing |
| 💡 Reflection Prompts | Personalised journaling suggestions based on recent entries |
| 🔄 Behavioral Loops | Trigger → thought → feeling → action → consequence mapping |

## Data Persistence

MindMirror stores all application data in a local SQLite database:

```text
mindmirror.db
```

Stored data includes:

- Journal entries with sentiment scores, emotions, and tags
- AI and local analysis reports
- Full chat history across multiple named sessions
- User profiles

Data survives browser refreshes, app restarts, and redeployments **as long as the SQLite database file is preserved**. Auto-login via URL parameters ensures your session persists through page refreshes.

## Privacy

- All journal data is stored locally in SQLite
- Journal text is only sent to Google Gemini when you explicitly run **AI Deep Analysis** or use **AI Chat**
- No data is shared with third parties beyond Gemini API calls
- No tracking, no analytics, no cookies

## Tech Stack

| Core | Libraries |
|---|---|
| Python 3.11 | Plotly *(charts & visualisation)* |
| Streamlit | Pandas *(data processing)* |
| Google Gemini API | google-generativeai *(Gemini SDK)* |
| SQLite | — |

## Project Structure

```text
.
├── .streamlit/
│   └── secrets.toml            # API key (not committed)
├── .gitignore                  # Git ignore rules
├── app.py                      # Main Streamlit app (UI, routing, pages)
├── analyzer.py                 # Sentiment analysis, Gemini AI calls
├── database.py                 # SQLite persistence layer
├── themes.py                   # 7 visual themes with CSS + Plotly colors
├── requirements.txt            # Python dependencies
├── mindmirror.db               # SQLite database (auto-created at runtime)
└── README.md                   # This file
```

## Deployment Notes

- The app is designed for **Streamlit Cloud** and local deployment
- On first deployment, startup may take longer due to dependency installation and database initialisation
- Subsequent loads are typically much faster
- If hosted on free Streamlit infrastructure, occasional cold-start delays are normal after inactivity
- Set your Gemini API key in **Settings → Secrets** on the Streamlit Cloud dashboard

## Who This Is For

Anyone interested in self-awareness, emotional intelligence, and personal growth — journalers, therapy clients, mindfulness practitioners, students, professionals managing stress, or anyone who wants to understand their own patterns better through the lens of AI-assisted behavioral analysis.

## Disclaimer

MindMirror AI provides **AI-generated psychological insights** for self-reflection and personal growth support. It does **not** constitute professional mental health advice, therapy, or diagnosis. If you are experiencing a mental health crisis, please contact a licensed professional or emergency services in your area. All AI-generated patterns, predictions, and recommendations should be considered as reflective tools, not clinical assessments.

---

<p align="center">
  <strong>MindMirror AI v2.0</strong> · Decode your mind · <a href="https://mindmirror-ai.streamlit.app">Try it live</a> · <a href="https://ai.google.dev">Powered by Google Gemini</a>
</p>
