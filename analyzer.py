# analyzer.py — MindMirror AI Analysis Engine v2
# (Gemini · Therapeutic Edition)
# STATUS: 🔄 FULLY REWRITTEN — replace your old file entirely

import re
import json
from collections import Counter

# ══════════════════════════════════════════════════════════════════
#  EMOTION LEXICON
# ══════════════════════════════════════════════════════════════════

LEXICON = {
    "happy": [
        "happy","joy","excited","great","wonderful","amazing",
        "fantastic","love","loved","cheerful","delighted","glad",
        "pleased","thrilled","elated","blissful","grateful",
        "thankful","optimistic","hopeful","proud","awesome",
        "brilliant","celebrate",
    ],
    "sad": [
        "sad","depressed","down","unhappy","miserable",
        "heartbroken","lonely","hopeless","disappointed","grief",
        "sorrow","melancholy","gloomy","despair","tearful","hurt",
        "empty","lost","crying","cried",
    ],
    "angry": [
        "angry","furious","annoyed","irritated","frustrated","mad",
        "rage","hostile","bitter","resentful","outraged","livid",
        "enraged","agitated","pissed","hate","hated",
    ],
    "anxious": [
        "anxious","worried","nervous","stressed","tense","uneasy",
        "restless","panicked","overwhelmed","fearful","afraid",
        "scared","dread","apprehensive","insecure","paranoid",
    ],
    "tired": [
        "tired","exhausted","drained","fatigued","burnt","burnout",
        "sleepy","weary","lethargic","depleted","spent","worn",
    ],
    "calm": [
        "calm","peaceful","relaxed","serene","tranquil","composed",
        "balanced","centered","mindful","comfortable","steady",
        "settled",
    ],
    "motivated": [
        "motivated","determined","driven","inspired","energized",
        "focused","ambitious","productive","empowered","confident",
        "unstoppable",
    ],
    "confused": [
        "confused","uncertain","unsure","indecisive","conflicted",
        "torn","puzzled","bewildered","doubtful","questioning",
        "unclear",
    ],
}

_POS = set(
    LEXICON["happy"] + LEXICON["calm"] + LEXICON["motivated"]
)
_NEG = set(
    LEXICON["sad"] + LEXICON["angry"]
    + LEXICON["anxious"] + LEXICON["tired"]
)

TOPIC_KEYS = {
    "work": [
        "work","job","office","boss","colleague","meeting",
        "project","deadline","career","promotion","salary",
        "coworker","client","manager","task","productivity",
        "hired","fired",
    ],
    "relationships": [
        "friend","family","partner","relationship","love",
        "dating","marriage","breakup","argument","fight","trust",
        "boyfriend","girlfriend","husband","wife","parent",
        "mother","father",
    ],
    "health": [
        "health","sick","doctor","exercise","gym","sleep","diet",
        "medication","pain","headache","tired","energy","weight",
        "fitness","therapy","hospital","anxiety","depression",
    ],
    "finance": [
        "money","bills","debt","savings","budget","expensive",
        "afford","financial","salary","payment","rent","income",
        "invest","broke","spending",
    ],
    "self_growth": [
        "learn","grow","improve","goal","habit","meditation",
        "mindfulness","therapy","journal","progress","change",
        "better","read","skill","develop",
    ],
    "creativity": [
        "create","art","write","music","design","idea",
        "inspiration","creative","project","hobby","paint",
        "draw","compose","sing",
    ],
    "social": [
        "party","event","gathering","social","people","crowd",
        "alone","isolated","lonely","hangout","friends","invite",
        "outing",
    ],
    "education": [
        "study","school","college","university","exam","class",
        "learn","course","assignment","grade","lecture","homework",
        "research",
    ],
}

_STOP = frozenset(
    "the a an is are was were be been being have has had do does "
    "did will would could should may might can shall to of in for "
    "on with at by from as into through during before after above "
    "below between out off over under again further then once "
    "here there when where why how all each every both few more "
    "most other some such no nor not only own same so than too "
    "very just because but and or if while about up it its i me "
    "my myself we our you your he him his she her they them their "
    "what which who whom this that these those am got get like "
    "feel felt really also much even still back way going went "
    "thing things today dont don't i'm it's i've ive im also "
    "been one two would been".split()
)


# ══════════════════════════════════════════════════════════════════
#  LOCAL ANALYSIS FUNCTIONS (unchanged logic)
# ══════════════════════════════════════════════════════════════════

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
    skip = {
        "The","This","That","These","Those","What","When",
        "Where","Who","Why","How","My","Your","His","Her",
        "Our","Their","Its","But","And","Monday","Tuesday",
        "Wednesday","Thursday","Friday","Saturday","Sunday",
        "January","February","March","April","May","June",
        "July","August","September","October","November",
        "December","Today","Yesterday","Tomorrow","Also",
        "After","Before","Still","Just","Then","Now","Later",
        "Very","Really","Maybe","Perhaps","So","Since",
        "Every","Each",
    }
    names = [
        w for w in re.findall(r"\b[A-Z][a-z]{2,}\b", text)
        if w not in skip
    ]
    days = [
        d.capitalize() for d in re.findall(
            r"\b(monday|tuesday|wednesday|thursday"
            r"|friday|saturday|sunday)\b", text, re.I)
    ]
    times = [
        t.lower() for t in re.findall(
            r"\b(morning|afternoon|evening|night"
            r"|midnight|dawn|dusk)\b", text, re.I)
    ]
    return {
        "people": list(set(names)),
        "days": list(set(days)),
        "times": list(set(times)),
    }


def extract_topics(text: str) -> dict:
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    found = {}
    for topic, kws in TOPIC_KEYS.items():
        n = len(words & set(kws))
        if n:
            found[topic] = n
    return dict(
        sorted(found.items(), key=lambda x: x[1], reverse=True)
    )


def word_frequencies(text: str, top_n: int = 25) -> list:
    words = re.findall(r"\b[a-z]+\b", text.lower())
    return Counter(
        w for w in words if w not in _STOP and len(w) > 2
    ).most_common(top_n)


def local_analysis(entries: list) -> dict | None:
    if not entries:
        return None
    all_text = " ".join(e["content"] for e in entries)

    sentiments = []
    for e in entries:
        s = sentiment_score(e["content"])
        sentiments.append({
            "date": e.get("entry_date", "?"),
            "score": s,
            "preview": e["content"][:120],
        })

    emotions = detect_emotions(all_text)
    ent_all = {"people": [], "days": [], "times": []}
    for e in entries:
        ents = extract_entities(e["content"])
        for k in ent_all:
            ent_all[k].extend(ents[k])

    return {
        "sentiments": sentiments,
        "avg_sentiment": round(
            sum(s["score"] for s in sentiments) / len(sentiments), 3
        ) if sentiments else 0,
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
#  GEMINI AI — THERAPEUTIC SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════

_ANALYSIS_SYSTEM = (
    "You are MindMirror — a deeply perceptive AI companion who "
    "blends the warmth of a trusted therapist with the analytical "
    "depth of a behavioral psychologist.\n\n"

    "YOUR VOICE:\n"
    "- Warm and gentle, like a wise friend sitting across from "
    "them with tea\n"
    "- Use 'I notice…', 'It seems like…', 'There is something "
    "interesting here…'\n"
    "- Celebrate small wins and growth, no matter how tiny\n"
    "- Acknowledge pain before analysing it\n"
    "- Never clinical, never cold, never preachy\n\n"

    "YOUR ANALYTICAL FRAMEWORK (use naturally — don't "
    "name-drop theories):\n"
    "- Cognitive patterns: all-or-nothing thinking, "
    "catastrophising, mind-reading, personalisation, 'should' "
    "statements, emotional reasoning, filtering out positives\n"
    "- Emotional regulation: how they handle difficult feelings, "
    "avoidance vs approach\n"
    "- Behavioral loops: trigger → thought → feeling → action → "
    "consequence → repeat\n"
    "- Attachment patterns: how they relate to others, trust, "
    "vulnerability\n"
    "- Values alignment: gap between what they want and what "
    "they do\n"
    "- Self-talk: inner critic vs inner ally, the language they "
    "use about themselves\n"
    "- Energy and capacity: what drains them, what fuels them\n"
    "- Time patterns: recurring cycles tied to days, people, "
    "or contexts\n"
    "- Narrative identity: the story they are telling about "
    "themselves\n\n"

    "RULES:\n"
    "- Ground EVERY insight in specific evidence from their "
    "entries — quote or reference them\n"
    "- Assign confidence: High / Medium / Low to each pattern\n"
    "- Be specific: 'You feel drained after evening calls with "
    "Sarah' NOT 'Social interactions affect you'\n"
    "- Predictions must be pattern-based, not generic\n"
    "- Recommendations must be small, doable, specific to "
    "their life\n"
    "- ALWAYS complete your full response. Never stop "
    "mid-sentence or mid-thought.\n"
    "- Do NOT hallucinate people or events not in the entries\n"
    "- Do NOT moralise or judge\n\n"

    "OUTPUT FORMAT (follow this structure):\n\n"

    "🔍 PATTERN SUMMARY\n"
    "- Key recurring themes:\n"
    "- Most frequent emotional states:\n"
    "- Overall emotional trajectory:\n\n"

    "📈 DETECTED PATTERNS\n"
    "1. [Pattern Title]\n"
    "   - What I see:\n"
    "   - Evidence from your entries:\n"
    "   - Confidence: High/Medium/Low\n"
    "(continue for each pattern — aim for 3-6)\n\n"

    "⏳ PREDICTIONS\n"
    "- In the coming days:\n"
    "- If this trajectory continues:\n\n"

    "🧠 DEEP INSIGHTS\n"
    "(2-4 insights that feel deeply personal)\n\n"

    "⚠️ TRIGGERS IDENTIFIED\n"
    "- Trigger → Emotional effect\n\n"

    "✅ GENTLE RECOMMENDATIONS\n"
    "(3-5 small, specific, doable suggestions)\n\n"

    "📊 META ANALYSIS\n"
    "- Emotional trend:\n"
    "- Behavioral stability:\n"
    "- Areas that need care:\n"
    "- Seeds of growth I see:"
)


_CHAT_SYSTEM = (
    "You are MindMirror — a warm, deeply perceptive AI "
    "companion. Think of yourself as the kind of therapist "
    "people wish they had: someone who truly listens, remembers "
    "everything, notices patterns with gentle brilliance, and "
    "never makes anyone feel judged.\n\n"

    "HOW YOU SPEAK:\n"
    "- Like a caring, wise friend — not a textbook\n"
    "- Warm, sometimes gently playful, always genuine\n"
    "- You say things like 'I notice something interesting…', "
    "'I am curious about that…', 'That makes a lot of sense "
    "actually…', 'Something I have been picking up across "
    "your entries…'\n"
    "- You validate feelings before exploring them ('That "
    "sounds really heavy' before 'Have you considered…')\n"
    "- You celebrate progress: 'Hey — did you notice you "
    "handled that differently this time?'\n"
    "- Keep responses natural and conversational\n"
    "- Sometimes end with a gentle question that invites "
    "reflection\n\n"

    "WHAT YOU DO:\n"
    "- Reference their actual journal entries naturally\n"
    "- Connect dots across entries they might not see\n"
    "- Gently surface blind spots without confrontation\n"
    "- Help them understand WHY they feel what they feel\n"
    "- Suggest small actions when appropriate\n"
    "- Track emotional shifts across the conversation\n"
    "- Remember everything shared in this chat session\n\n"

    "YOUR PSYCHOLOGICAL TOOLKIT (use naturally, never "
    "name-drop):\n"
    "- Cognitive reframing\n"
    "- Emotional validation\n"
    "- Pattern interruption\n"
    "- Strengths spotting\n"
    "- Values exploration\n"
    "- Behavioral experiments as invitations\n\n"

    "WHAT YOU NEVER DO:\n"
    "- Sound robotic or clinical or like a generic chatbot\n"
    "- Give motivational poster advice\n"
    "- Judge, moralise, or lecture\n"
    "- Start with 'That is a great question!'\n"
    "- Make assumptions beyond what they have written\n"
    "- Leave a response unfinished — ALWAYS complete your "
    "full thought\n"
    "- Use bullet points unless specifically asked"
)


_REFLECTION_SYSTEM = (
    "You are MindMirror, a warm and perceptive journaling "
    "companion.\n\n"
    "Based on the user's recent journal entries, generate 3 "
    "deeply personalised reflection prompts they should explore "
    "next. Each prompt should:\n"
    "- Connect to specific themes or patterns you see\n"
    "- Invite deeper self-exploration\n"
    "- Feel like a caring therapist gently nudging toward "
    "insight\n"
    "- Include a brief warm explanation of why this prompt "
    "matters for them\n\n"
    "Write conversationally. ALWAYS complete your full response."
)


# ══════════════════════════════════════════════════════════════════
#  GEMINI HELPER
# ══════════════════════════════════════════════════════════════════

def _make_model(api_key, model_name, system_instruction=None):
    """Create a configured Gemini GenerativeModel."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    kwargs = {"model_name": model_name}
    if system_instruction:
        kwargs["system_instruction"] = system_instruction

    return genai.GenerativeModel(**kwargs)


# ══════════════════════════════════════════════════════════════════
#  AI ANALYSIS
# ══════════════════════════════════════════════════════════════════

def ai_analysis(entries, api_key, model="gemini-2.5-flash",
                local_ctx=None):
    """Run deep AI analysis on journal entries."""
    entry_text = ""
    for i, e in enumerate(entries, 1):
        d = e.get("entry_date", "undated")
        entry_text += (
            f"\n--- Entry {i} ({d}) ---\n{e['content']}\n"
        )

    ctx = ""
    if local_ctx:
        ctx = (
            f"\n[LOCAL METRICS] "
            f"avg_sentiment={local_ctx['avg_sentiment']}, "
            f"emotions={list(local_ctx['emotions'].keys())}, "
            f"topics={list(local_ctx['topics'].keys())}, "
            f"people={local_ctx['people']}, "
            f"entries={local_ctx['entry_count']}\n"
        )

    try:
        mdl = _make_model(
            api_key, model,
            system_instruction=_ANALYSIS_SYSTEM,
        )
        response = mdl.generate_content(
            f"Here are the journal entries to analyse:"
            f"{ctx}\n{entry_text}",
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 8192,
            },
        )
        return response.text
    except Exception as exc:
        return f"⚠️ Analysis error: {exc}"


# ══════════════════════════════════════════════════════════════════
#  AI CHAT (multi-turn with Gemini Chat API)
# ══════════════════════════════════════════════════════════════════

def ai_chat(message, entries, history, api_key,
            model="gemini-2.5-flash"):
    """Chat with Gemini about the user's patterns."""
    entry_ctx = ""
    for i, e in enumerate(entries[-15:], 1):
        entry_ctx += (
            f"\nEntry {i} ({e.get('entry_date','?')}): "
            f"{e['content'][:350]}"
        )

    sys_prompt = (
        _CHAT_SYSTEM
        + "\n\n=== USER'S JOURNAL ENTRIES ===\n"
        + entry_ctx
    )

    try:
        mdl = _make_model(
            api_key, model,
            system_instruction=sys_prompt,
        )

        gemini_history = []
        for m in history[-30:]:
            gemini_history.append({
                "role": (
                    "user" if m["role"] == "user" else "model"
                ),
                "parts": [m["content"]],
            })

        chat = mdl.start_chat(history=gemini_history)
        response = chat.send_message(
            message,
            generation_config={
                "temperature": 0.75,
                "max_output_tokens": 4096,
            },
        )
        return response.text
    except Exception as exc:
        return f"⚠️ Chat error: {exc}"


# ══════════════════════════════════════════════════════════════════
#  AI REFLECTION PROMPTS
# ══════════════════════════════════════════════════════════════════

def ai_reflection_prompts(entries, api_key,
                          model="gemini-2.5-flash"):
    """Generate personalised reflection prompts."""
    recent = "\n".join(
        f"({e.get('entry_date','?')}): {e['content'][:300]}"
        for e in entries[-5:]
    )
    try:
        mdl = _make_model(
            api_key, model,
            system_instruction=_REFLECTION_SYSTEM,
        )
        response = mdl.generate_content(
            f"Here are my recent journal entries:\n{recent}",
            generation_config={
                "temperature": 0.8,
                "max_output_tokens": 1000,
            },
        )
        return response.text
    except Exception as exc:
        return f"Could not generate prompts: {exc}"
