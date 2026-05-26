[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)](#)

# MindMirror AI v3.0

**Your AI companion for self-discovery, emotional growth, and everyday mental wellness.**

MindMirror AI is a warm, human-sounding journaling companion that helps you understand your emotional patterns, build resilience, and grow at your own pace. Powered by Google Gemini and built with Streamlit, it combines structured therapeutic tools with gentle AI guidance -- never robotic, never clinical, always on your side.

<p align="center">
  <a href="https://mindmirror-ai.streamlit.app">
    <img src="https://img.shields.io/badge/Launch%20App-MindMirror%20AI%20Live-059669?style=for-the-badge&logoColor=white" alt="Launch MindMirror AI">
  </a>
</p>

<p align="center">
  <a href="https://mindmirror-ai.streamlit.app">https://mindmirror-ai.streamlit.app</a>
</p>

---

## Features

### Secure Authentication

- Password-based registration and login (hashed credentials, no plaintext)
- Brute-force protection (lockout after 5 failed attempts in 15 minutes)
- No URL parameter login -- sessions stay in secure server-side state

### Personalized Onboarding

- 4-step onboarding wizard when you first sign up
- Choose your core values, preferred support style, emotional landscape, and privacy comfort level
- The AI remembers your preferences and adapts its tone accordingly

### Journaling

- **5 journal templates**: Freeform, Thought Record (CBT), Gratitude, Evening Review, Body Check-In
- **Live cognitive distortion detection** as you write -- gentle highlights, not judgments
- **Batch import** with automatic tagging for bringing in past notes
- Sentiment scoring and emotion tagging on every save

### AI Deep Analysis

- 9-section behavioral report covering patterns, triggers, cognitive loops, emotional trajectories, and personalized recommendations
- Context-aware -- draws from your journal history, goals, and check-in data

### AI Chat

- **5 therapeutic modes**: Open, CBT, Validation, Reflection, Check-in
- **Empathy level control** (1-10) so you set how warm or direct the AI sounds
- **Crisis detection** -- if you share something urgent, MindMirror surfaces crisis resources immediately
- Multi-turn memory with full journal and analysis context

### Dashboard & Insights

- Mood and energy timeline charts
- Emotional fingerprint radar showing your dominant patterns
- Growth radar tracking progress across dimensions
- **Daily emoji check-in** for quick mood snapshots
- **Goal tracking** with visual progress indicators
- **PHQ-9 and GAD-7** structured mental health check-ins
- **AI mood forecast** and narrative summaries of your week

### Skills & Growth

- **4 skill module categories**: Mindfulness, Distress Tolerance, Self-Compassion, Cognitive Skills
- **4 reflection journeys**: Heartbreak Recovery, Motivation Building, Anxiety Management, Self-Worth
- Quick grounding tools and guided breathing exercises
- Contextual skill recommendations based on your recent entries

### Personalization & Accessibility

- **7 visual themes** with adaptive mood tinting (Deep Ocean, Sakura, Forest, Cosmic Purple, Sunrise, Midnight, Clean Light)
- Font scaling for comfortable reading
- High contrast mode
- Reduce motion option for vestibular sensitivity

### Data & Privacy

- **Full data export** in JSON and CSV formats
- **Backup and restore** your entire account
- Rate limiting (20 AI calls per 10 minutes) to prevent abuse
- Input sanitization (XSS prevention) on all user-submitted text
- All data stored locally in SQLite -- nothing shared beyond Gemini API calls

---

## Navigation

The app is organized into 7 top-level pages:

| Page | Purpose |
|---|---|
| Journal | Write entries using 5 templates, batch import, browse and manage past entries |
| Analysis | Local pattern detection + AI deep 9-section behavioral analysis |
| AI Chat | Therapeutic conversations with 5 modes, empathy control, and crisis detection |
| Dashboard | Mood timelines, emotional fingerprint, growth radar, check-ins, goals, PHQ-9/GAD-7 |
| Skills & Growth | Skill modules, reflection journeys, grounding tools, breathing guide |
| History | Browse saved analyses, chat transcripts, and export data |
| Settings | API key status, theme selection, accessibility options, backup/restore, danger zone |

---

## Quick Start

### Try it now

Visit **[mindmirror-ai.streamlit.app](https://mindmirror-ai.streamlit.app)** -- no installation needed. Create an account with a username and password to get started.

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

On first launch, register with a username and password (minimum 6 characters). The onboarding wizard will guide you through personalizing your experience.

Get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey), or set it in **Settings > Secrets** on the Streamlit Cloud dashboard.

---

## Privacy & Security

- Passwords are hashed before storage -- never stored in plaintext
- No URL parameters carry authentication state
- Journal text is only sent to Google Gemini when you explicitly use AI features (Deep Analysis, AI Chat, mood forecast)
- All user inputs are sanitized to prevent XSS
- Rate limiting protects against API abuse
- No tracking, no analytics, no cookies, no third-party data sharing
- Full data export and account deletion available in Settings

---

## Tech Stack

| Core | Libraries |
|---|---|
| Python 3.11 | Plotly *(charts & visualization)* |
| Streamlit | Pandas *(data processing)* |
| Google Gemini API | NumPy *(numerical operations)* |
| SQLite | google-generativeai *(Gemini SDK)* |

---

## Project Structure

```text
.
├── .streamlit/
│   ├── config.toml             # Server and theme configuration
│   └── secrets.toml            # API key (not committed)
├── .gitignore                  # Git ignore rules
├── app.py                      # Main Streamlit app (UI, routing, all pages)
├── analyzer.py                 # NLP, sentiment analysis, Gemini AI calls
├── database.py                 # SQLite persistence, auth, rate limiting
├── themes.py                   # 7 visual themes with CSS + Plotly colors
├── backup.py                   # Data export, import, backup and restore
├── requirements.txt            # Python dependencies
├── CHANGELOG.md                # Version history
├── mindmirror.db               # SQLite database (auto-created at runtime)
└── README.md                   # This file
```

---

## Deployment Notes

- Designed for **Streamlit Cloud** and local deployment
- On first deployment, startup may take longer due to dependency installation and database initialization
- Set your Gemini API key in **Settings > Secrets** on the Streamlit Cloud dashboard
- The app runs without an API key for local-only features (journaling, dashboard, skills)

---

## Disclaimer

MindMirror AI is a **self-reflection and personal growth tool**. It is not a substitute for professional mental health care, therapy, or diagnosis. If you are experiencing a mental health crisis, please contact a licensed professional or emergency services in your area. The AI-generated insights, patterns, and suggestions are reflective tools to support your journey -- not clinical assessments.

---

<p align="center">
  <strong>MindMirror AI v3.0</strong> -- Understand yourself, one entry at a time -- <a href="https://mindmirror-ai.streamlit.app">Try it live</a>
</p>
