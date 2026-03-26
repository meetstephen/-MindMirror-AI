# analyzer.py — MindMirror AI Analysis Engine (Gemini Edition)

import re, json
from collections import Counter
from datetime import datetime

# ── Emotion lexicon ──────────────────────────────────────────────
LEXICON = {
    "happy":     ["happy","joy","excited","great","wonderful","amazing","fantastic","love","loved",
                   "cheerful","delighted","glad","pleased","thrilled","elated","blissful","grateful",
                   "thankful","optimistic","hopeful","proud","awesome","brilliant","celebrate"],
    "sad":       ["sad","depressed","down","unhappy","miserable","heartbroken","lonely","hopeless",
                   "disappointed","grief","sorrow","melancholy","gloomy","despair","tearful","hurt",
                   "empty","lost","crying","cried"],
    "angry":     ["angry","furious","annoyed","irritated","frustrated","mad","rage","hostile","bitter",
                   "resentful","outraged","livid","enraged","agitated","pissed","hate","hated"],
    "anxious":   ["anxious","worried","nervous","stressed","tense","uneasy","restless","panicked",
                   "overwhelmed","fearful","afraid","scared","dread","apprehensive","insecure","paranoid"],
    "tired":     ["tired","exhausted","drained","fatigued","burnt","burnout","sleepy","weary",
                   "lethargic","depleted","spent","worn"],
    "calm":      ["calm","peaceful","relaxed","serene","tranquil","composed","balanced","centered",
                   "mindful","comfortable","steady","settled"],
    "motivated": ["motivated","determined","driven","inspired","energized","focused","ambitious",
                   "productive","empowered","confident","unstoppable"],
    "confused":  ["confused","uncertain","unsure","indecisive","conflicted","torn","puzzled",
                   "bewildered","doubtful","questioning","unclear"],
}

_POS = set(LEXICON["happy"] + LEXICON["calm"] + LEXICON["motivated"])
_NEG = set(LEXICON["sad"] + LEXICON["angry"] + LEXICON["anxious"] + LEXICON["tired"])

TOPIC_KEYS = {
    "work":          ["work","job","office","boss","colleague","meeting","project","deadline","career",
                      "promotion","salary","coworker","client","manager","task","productivity","hired","fired"],
    "relationships": ["friend","family","partner","relationship","love","dating","marriage","breakup",
                      "argument","fight","trust","boyfriend","girlfriend","husband","wife","parent","mother","father"],
    "health":        ["health","sick","doctor","exercise","gym","sleep","diet","medication","pain",
                      "headache","tired","energy","weight","fitness","therapy","hospital","anxiety","depression"],
    "finance":       ["money","bills","debt","savings","budget","expensive","afford","financial",
                      "salary","payment","rent","income","invest","broke","spending"],
    "self_growth":   ["learn","grow","improve","goal","habit","meditation","mindfulness","therapy",
                      "journal","progress","change","better","read","skill","develop"],
    "creativity":    ["create","art","write","music","design","idea","inspiration","creative",
                      "project","hobby","paint","draw","compose","sing"],
    "social":        ["party","event","gathering","social","people","crowd","alone","isolated",
                      "lonely","hangout","friends","invite","outing"],
    "education":     ["study","school","college","university","exam","class","learn","course",
                      "assignment","grade","lecture","homework","research"],
}

_STOP = frozenset(
    "the a an is are was were be been being have has had do does did will would could should "
    "may might can shall to of in for on with at by from as into through during before after "
    "above below between out off over under again further then once here there when where why "
    "how all each every both few more most other some such no nor not only own same so than too "
    "very just because but and or if while about up it its i me my myself we our you your he "
    "him his she her they them their what which who whom this that these those am got get like "
    "feel felt really also much even still back way going went thing things today dont don't "
    "i'm it's i've ive im also been one two would been".split()
)

# ── Local functions ──────────────────────────────────────────────

def sentiment_score(text: str) -> float:
    words = re.findall(r"\b[a-z]+\b", text.lower())
    if not words:
        return 0.0
    p = sum(1 for w in words if w in _POS)
    n = sum(1 for w in words if w in _NEG)
    total = p + n
    return round((p - n) / total, 3) if total else 0.0


def detect_emotions(text: str) -> dict:
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    found = {}
    for emo, kws in LEXICON.items():
        hits = words & set(kws)
        if hits:
            found[emo] = sorted(hits)
    return found


def extract_entities(text: str) -> dict:
    skip = {"The","This","That","These","Those","What","When","Where","Who","Why","How",
            "My","Your","His","Her","Our","Their","Its","But","And","Monday","Tuesday",
            "Wednesday","Thursday","Friday","Saturday","Sunday","January","February","March",
            "April","May","June","July","August","September","October","November","December",
            "Today","Yesterday","Tomorrow","Also","After","Before","Still","Just","Then",
            "Now","Later","Very","Really","Maybe","Perhaps","So","Since","Every","Each"}
    names = [w for w in re.findall(r"\b[A-Z][a-z]{2,}\b", text) if w not in skip]
    days = [d.capitalize() for d in re.findall(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", text, re.I)]
    times = [t.lower() for t in re.findall(
        r"\b(morning|afternoon|evening|night|midnight|dawn|dusk)\b", text, re.I)]
    return {"people": list(set(names)), "days": list(set(days)), "times": list(set(times))}


def extract_topics(text: str) -> dict:
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    found = {}
    for topic, kws in TOPIC_KEYS.items():
        n = len(words & set(kws))
        if n:
            found[topic] = n
    return dict(sorted(found.items(), key=lambda x: x[1], reverse=True))


def word_frequencies(text: str, top_n: int = 25) -> list:
    words = re.findall(r"\b[a-z]+\b", text.lower())
    return Counter(w for w in words if w not in _STOP and len(w) > 2).most_common(top_n)


# ── Aggregate local analysis ────────────────────────────────────

def local_analysis(entries: list) -> dict | None:
    if not entries:
        return None
    all_text = " ".join(e["content"] for e in entries)

    sentiments = []
    for e in entries:
        s = sentiment_score(e["content"])
        sentiments.append({"date": e.get("entry_date", "?"), "score": s,
                           "preview": e["content"][:120]})

    emotions = detect_emotions(all_text)
    ent_all = {"people": [], "days": [], "times": []}
    for e in entries:
        ents = extract_entities(e["content"])
        for k in ent_all:
            ent_all[k].extend(ents[k])

    return {
        "sentiments": sentiments,
        "avg_sentiment": round(sum(s["score"] for s in sentiments) / len(sentiments), 3) if sentiments else 0,
        "emotions": emotions,
        "people": Counter(ent_all["people"]).most_common(10),
        "days": Counter(ent_all["days"]).most_common(7),
        "times": Counter(ent_all["times"]).most_common(),
        "topics": extract_topics(all_text),
        "words": word_frequencies(all_text),
        "entry_count": len(entries),
        "emotion_diversity": len(emotions),
    }


# ══════════════════════════════════════════════════════════════════
#  GEMINI AI FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _get_gemini_model(api_key: str, model_name: str):
    """Initialise and return a Gemini GenerativeModel."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


# ── System prompts ───────────────────────────────────────────────

_SYSTEM_ANALYSIS = """You are an advanced AI behavioral analyst, cognitive pattern detector, and emotional intelligence engine.

Analyze the journal entries below and produce a structured report. Rules:
• Do NOT hallucinate people/entities not mentioned.
• Do NOT give generic self-help advice. Be specific and evidence-based.
• Do NOT moralize or judge.
• Assign confidence: High / Medium / Low to each pattern.
• Reference specific entries as evidence.

OUTPUT FORMAT (use exactly):

🔍 PATTERN SUMMARY
- Key recurring themes:
- Most frequent emotional states:

📈 DETECTED PATTERNS
1. [Pattern Title]
   - Description:
   - Evidence:
   - Confidence:
(repeat for each pattern)

⏳ PREDICTIONS
- Short-term:
- Long-term:

🧠 DEEP INSIGHTS
- Insight 1:
- Insight 2:

⚠️ TRIGGERS IDENTIFIED
- Trigger → Effect

✅ ACTIONABLE RECOMMENDATIONS
1.
2.

📊 META ANALYSIS
- Emotional trend:
- Behavioral stability:
- Risk areas:
- Growth areas:"""


_SYSTEM_CHAT = """You are MindMirror AI — an empathetic behavioral analyst and personal insight companion.
You have access to the user's journal entries provided below.
Rules:
• Be insightful, warm, and specific.
• Reference the user's actual entries when relevant.
• Never give generic advice — all responses must be grounded in their data.
• If the user asks about patterns, reference concrete evidence from their journal.
• Keep responses focused and clear."""


# ── AI-powered analysis ─────────────────────────────────────────

def ai_analysis(entries: list, api_key: str, model: str = "gemini-2.0-flash",
                local_ctx: dict | None = None) -> str:
    """Run deep AI analysis on journal entries using Gemini."""

    entry_text = ""
    for i, e in enumerate(entries, 1):
        d = e.get("entry_date", "undated")
        entry_text += f"\n--- Entry {i} ({d}) ---\n{e['content']}\n"

    ctx = ""
    if local_ctx:
        ctx = (f"\n[LOCAL METRICS] avg_sentiment={local_ctx['avg_sentiment']}, "
               f"emotions={list(local_ctx['emotions'].keys())}, "
               f"topics={list(local_ctx['topics'].keys())}, "
               f"people={local_ctx['people']}, entries={local_ctx['entry_count']}\n")

    full_prompt = (
        f"{_SYSTEM_ANALYSIS}\n\n"
        f"Now analyze these journal entries:{ctx}\n{entry_text}"
    )

    try:
        model_obj = _get_gemini_model(api_key, model)
        response = model_obj.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 4000,
            }
        )
        return response.text
    except Exception as exc:
        return f"⚠️ Gemini AI analysis error: {exc}"


# ── AI chat ──────────────────────────────────────────────────────

def ai_chat(message: str, entries: list, history: list, api_key: str,
            model: str = "gemini-2.0-flash") -> str:
    """Chat with Gemini about the user's patterns."""

    # Build journal context from recent entries
    entry_ctx = ""
    for i, e in enumerate(entries[-12:], 1):
        entry_ctx += f"\nEntry {i} ({e.get('entry_date','?')}): {e['content'][:300]}"

    # Build conversation history string
    history_text = ""
    for m in history[-24:]:
        role_label = "User" if m["role"] == "user" else "MindMirror AI"
        history_text += f"\n{role_label}: {m['content']}"

    full_prompt = (
        f"{_SYSTEM_CHAT}\n\n"
        f"=== USER'S JOURNAL ENTRIES ===\n{entry_ctx}\n\n"
        f"=== CONVERSATION HISTORY ===\n{history_text}\n\n"
        f"User: {message}\n\n"
        f"MindMirror AI:"
    )

    try:
        model_obj = _get_gemini_model(api_key, model)
        response = model_obj.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1500,
            }
        )
        return response.text
    except Exception as exc:
        return f"⚠️ Gemini chat error: {exc}"


# ── AI reflection prompts ───────────────────────────────────────

def ai_reflection_prompts(entries: list, api_key: str,
                          model: str = "gemini-2.0-flash") -> str:
    """Generate personalised reflection prompts based on recent entries."""

    recent = "\n".join(
        f"({e.get('entry_date','?')}): {e['content'][:250]}"
        for e in entries[-5:]
    )

    prompt = (
        "Based on these recent journal entries, generate 3 thoughtful and deeply "
        "personalised reflection prompts the user should journal about next.\n"
        "Be specific to their situation — not generic.\n"
        "Format: numbered list with a brief explanation of why each prompt matters.\n\n"
        f"Recent entries:\n{recent}"
    )

    try:
        model_obj = _get_gemini_model(api_key, model)
        response = model_obj.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,
                "max_output_tokens": 500,
            }
        )
        return response.text
    except Exception as exc:
        return f"Could not generate prompts: {exc}"
