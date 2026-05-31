# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — analyzer.py  PART 1 of 2  (v3 · Enhanced)     ║
# ║  CHUNK 2 of 10                                                  ║
# ║  Core NLP: sentiment, emotions, entities, topics, word freq,    ║
# ║  cognitive distortions, crisis detection, Big Five hints,       ║
# ║  emotional granularity, growth metric helpers                   ║
# ╚══════════════════════════════════════════════════════════════════╝

import re
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════════
#  EMOTION LEXICON (expanded for granularity)
# ══════════════════════════════════════════════════════════════════

EMOTION_LEXICON = {
    # ── Joy family ───────────────────────────────────────────────
    "joy": [
        "happy", "joy", "joyful", "delighted", "cheerful",
        "elated", "thrilled", "ecstatic", "blissful", "glad",
        "pleased", "content", "satisfied", "euphoric", "radiant",
        "wonderful", "amazing", "fantastic", "great", "awesome",
        "love", "loving", "beloved", "adore", "cherish",
        "excited", "exciting", "enthusiasm", "enthusiastic",
        "playful", "fun", "laugh", "laughing", "smile", "smiling",
        "celebrate", "celebration", "proud", "pride", "triumph",
        "grateful", "thankful", "blessed", "appreciate",
        "hopeful", "optimistic", "inspired", "inspiring",
    ],
    # ── Sadness family ───────────────────────────────────────────
    "sadness": [
        "sad", "sadness", "unhappy", "miserable", "depressed",
        "depression", "down", "gloomy", "gloom", "melancholy",
        "heartbroken", "heartbreak", "grief", "grieving",
        "mourning", "loss", "lost", "lonely", "loneliness",
        "alone", "isolated", "isolation", "abandoned",
        "empty", "emptiness", "hollow", "numb", "numbness",
        "hopeless", "despair", "despairing", "desolate",
        "disappointed", "disappointing", "disappointment",
        "discouraged", "disheartened", "defeated",
        "tearful", "tears", "crying", "cry", "weep", "sobbing",
        "homesick", "nostalgic", "wistful", "yearning",
    ],
    # ── Anger family ─────────────────────────────────────────────
    "anger": [
        "angry", "anger", "furious", "rage", "raging", "mad",
        "irritated", "irritation", "annoyed", "annoying",
        "frustrated", "frustration", "aggravated", "agitated",
        "hostile", "hostility", "resentful", "resentment",
        "bitter", "bitterness", "outraged", "outrage",
        "livid", "fuming", "enraged", "infuriated",
        "hate", "hatred", "loathe", "loathing", "despise",
        "disgusted", "disgust", "repulsed", "revolted",
        "contempt", "scorn", "indignant", "indignation",
        "jealous", "jealousy", "envious", "envy",
    ],
    # ── Fear / anxiety family ────────────────────────────────────
    "fear": [
        "afraid", "fear", "fearful", "scared", "terrified",
        "terror", "panic", "panicking", "panicked", "dread",
        "anxious", "anxiety", "worried", "worry", "worrying",
        "nervous", "nervousness", "uneasy", "unease",
        "apprehensive", "apprehension", "tense", "tension",
        "stressed", "stress", "stressful", "overwhelmed",
        "overwhelm", "frantic", "alarmed", "alarm",
        "insecure", "insecurity", "vulnerable", "threatened",
        "paranoid", "paranoia", "phobia", "claustrophobic",
        "restless", "on edge", "jittery", "shaky",
    ],
    # ── Surprise ─────────────────────────────────────────────────
    "surprise": [
        "surprised", "surprise", "shocking", "shocked",
        "astonished", "astonishment", "amazed", "amazement",
        "stunned", "startled", "unexpected", "unexpectedly",
        "disbelief", "unbelievable", "bewildered", "baffled",
        "mind-blown", "speechless", "awestruck", "awe",
        "flabbergasted", "dumbfounded", "perplexed",
    ],
    # ── Trust / safety ───────────────────────────────────────────
    "trust": [
        "trust", "trusting", "trustworthy", "safe", "safety",
        "secure", "security", "comfortable", "comfort",
        "reassured", "confident", "confidence", "faith",
        "reliable", "dependable", "loyal", "loyalty",
        "honest", "honesty", "genuine", "authentic",
        "supported", "supportive", "understood",
        "accepted", "belonging", "connected", "connection",
    ],
    # ── Shame / guilt ────────────────────────────────────────────
    "shame": [
        "ashamed", "shame", "shameful", "embarrassed",
        "embarrassment", "humiliated", "humiliation",
        "guilty", "guilt", "regret", "regretful", "remorse",
        "mortified", "self-conscious", "inadequate",
        "unworthy", "worthless", "pathetic", "failure",
        "stupid", "idiot", "useless", "incompetent",
        "blame", "blaming", "self-blame",
    ],
    # ── Exhaustion / burnout ─────────────────────────────────────
    "exhaustion": [
        "exhausted", "exhaustion", "tired", "fatigue",
        "fatigued", "drained", "burned out", "burnout",
        "depleted", "worn out", "weary", "lethargic",
        "sluggish", "spent", "overworked", "overwhelmed",
        "no energy", "can't keep up", "running on empty",
    ],
    # ── Confusion ────────────────────────────────────────────────
    "confusion": [
        "confused", "confusion", "uncertain", "uncertainty",
        "unsure", "unclear", "lost", "disoriented",
        "conflicted", "torn", "ambivalent", "indecisive",
        "puzzled", "perplexed", "bewildered", "foggy",
        "don't know", "mixed feelings", "contradictory",
    ],
}

# Granularity map: sub-emotions → parent
EMOTION_GRANULARITY = {
    "joy": {
        "gratitude": ["grateful", "thankful", "blessed", "appreciate"],
        "excitement": ["excited", "thrilled", "ecstatic", "enthusiastic"],
        "contentment": ["content", "satisfied", "peaceful", "serene"],
        "pride": ["proud", "pride", "accomplished", "triumph"],
        "love": ["love", "loving", "adore", "cherish", "beloved"],
        "hope": ["hopeful", "optimistic", "inspired", "encouraging"],
        "amusement": ["fun", "funny", "laugh", "playful", "hilarious"],
    },
    "sadness": {
        "grief": ["grief", "grieving", "mourning", "loss", "bereavement"],
        "loneliness": ["lonely", "alone", "isolated", "abandoned"],
        "disappointment": ["disappointed", "let down", "discouraged"],
        "despair": ["hopeless", "despair", "desolate", "empty"],
        "nostalgia": ["nostalgic", "homesick", "wistful", "yearning"],
        "melancholy": ["melancholy", "gloomy", "somber", "blue"],
    },
    "anger": {
        "frustration": ["frustrated", "frustration", "aggravated"],
        "resentment": ["resentful", "resentment", "bitter"],
        "irritation": ["irritated", "annoyed", "aggravated"],
        "rage": ["furious", "rage", "livid", "enraged"],
        "jealousy": ["jealous", "envious", "envy"],
        "disgust": ["disgusted", "repulsed", "revolted"],
    },
    "fear": {
        "anxiety": ["anxious", "anxiety", "worried", "nervous"],
        "stress": ["stressed", "stressful", "overwhelmed", "pressure"],
        "dread": ["dread", "dreading", "apprehensive"],
        "panic": ["panic", "panicking", "frantic"],
        "insecurity": ["insecure", "inadequate", "self-doubt"],
    },
}


# ══════════════════════════════════════════════════════════════════
#  SENTIMENT LEXICON (AFINN-inspired, expanded)
# ══════════════════════════════════════════════════════════════════

_POS_WORDS = {
    "good": 3, "great": 3, "excellent": 4, "amazing": 4,
    "wonderful": 4, "fantastic": 4, "awesome": 4,
    "happy": 3, "love": 3, "beautiful": 3, "best": 4,
    "perfect": 4, "enjoy": 2, "enjoying": 2, "enjoyed": 2,
    "fun": 2, "glad": 2, "pleased": 2, "proud": 3,
    "grateful": 3, "thankful": 3, "blessed": 3,
    "hopeful": 2, "optimistic": 2, "confident": 2,
    "peaceful": 3, "calm": 2, "relaxed": 2, "serene": 3,
    "excited": 3, "thrilled": 3, "delighted": 3,
    "inspired": 3, "motivated": 2, "energized": 2,
    "accomplished": 3, "succeed": 3, "success": 3,
    "improved": 2, "progress": 2, "growth": 2,
    "strong": 2, "brave": 2, "courage": 3,
    "kind": 2, "generous": 2, "compassionate": 3,
    "laugh": 2, "smile": 2, "warmth": 2, "cozy": 2,
    "triumph": 3, "victory": 3, "celebrate": 3,
    "bright": 2, "vibrant": 2, "alive": 2,
    "comfortable": 2, "safe": 2, "secure": 2,
    "free": 2, "liberated": 3, "relief": 2, "relieved": 2,
    "connected": 2, "supported": 2, "understood": 2,
    "creative": 2, "productive": 2, "focused": 2,
    "better": 1, "nice": 1, "fine": 1, "okay": 0.5,
    "well": 1, "like": 1, "liked": 1,
}

_NEG_WORDS = {
    "bad": -3, "terrible": -4, "awful": -4, "horrible": -4,
    "worst": -4, "hate": -3, "hated": -3, "ugly": -2,
    "sad": -2, "unhappy": -2, "miserable": -4,
    "depressed": -3, "depression": -3, "anxious": -2,
    "anxiety": -2, "worried": -2, "stress": -2,
    "stressed": -3, "angry": -3, "furious": -4,
    "frustrated": -2, "frustration": -2, "annoyed": -2,
    "scared": -2, "afraid": -2, "fear": -2, "terrified": -4,
    "lonely": -3, "alone": -1, "isolated": -3,
    "exhausted": -3, "tired": -1, "drained": -3,
    "burnout": -3, "overwhelmed": -3, "panic": -3,
    "hopeless": -4, "despair": -4, "empty": -2,
    "guilty": -2, "ashamed": -3, "shame": -3,
    "worthless": -4, "useless": -3, "pathetic": -4,
    "failure": -3, "failed": -2, "failing": -2,
    "hurt": -2, "pain": -2, "painful": -3, "suffering": -3,
    "cry": -2, "crying": -2, "tears": -2,
    "heartbroken": -4, "devastated": -4,
    "confused": -1, "lost": -1, "uncertain": -1,
    "rejected": -3, "abandoned": -3, "betrayed": -4,
    "jealous": -2, "envious": -2, "resentful": -2,
    "disgusted": -3, "numb": -2, "dead inside": -4,
    "broken": -3, "shattered": -4, "ruined": -3,
    "worse": -2, "wrong": -1, "boring": -1,
    "irritated": -2, "agitated": -2, "hostile": -3,
    "regret": -2, "remorse": -2, "mistake": -1,
    "struggle": -1, "struggling": -2, "difficult": -1,
    "hard": -1, "tough": -1, "rough": -1,
    "sick": -2, "ill": -1, "unwell": -2,
    "insomnia": -2, "nightmare": -3, "restless": -1,
}

_NEGATION_WORDS = {
    "not", "no", "never", "neither", "nobody", "nothing",
    "nowhere", "nor", "cannot", "can't", "won't", "wouldn't",
    "shouldn't", "couldn't", "don't", "doesn't", "didn't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't",
    "haven't", "hadn't", "barely", "hardly", "scarcely",
}

_INTENSIFIERS = {
    "very": 1.5, "extremely": 2.0, "incredibly": 2.0,
    "really": 1.3, "so": 1.4, "absolutely": 1.8,
    "totally": 1.5, "completely": 1.6, "deeply": 1.5,
    "utterly": 1.8, "terribly": 1.6, "awfully": 1.5,
    "quite": 1.2, "rather": 1.1, "pretty": 1.2,
    "super": 1.5, "especially": 1.3,
}


# ══════════════════════════════════════════════════════════════════
#  COGNITIVE DISTORTION PATTERNS
# ══════════════════════════════════════════════════════════════════

COGNITIVE_DISTORTIONS = {
    "catastrophizing": {
        "label": "Catastrophizing",
        "description": "Expecting the worst possible outcome",
        "reframe": "What's the most realistic outcome? What evidence supports a less extreme view?",
        "patterns": [
            r"\b(everything is|it'?s all) (ruined|over|falling apart|destroyed)\b",
            r"\b(worst|terrible|horrible|catastroph|disaster|end of the world)\b.*\b(ever|always|going to)\b",
            r"\bwhat if .*(worst|terrible|die|never|ruin|destroy)\b",
            r"\b(never going to|will never|can never)\b.*\b(recover|get better|be okay|succeed|work out)\b",
            r"\b(the world is ending|life is over|nothing will ever)\b",
            r"\b(completely|totally|absolutely) (ruined|destroyed|hopeless|over)\b",
            r"\b(can'?t survive|won'?t survive|can'?t handle)\b",
            r"\bno way out\b",
        ],
    },
    "all_or_nothing": {
        "label": "All-or-Nothing Thinking",
        "description": "Seeing things in black and white, with no middle ground",
        "reframe": "Is there a middle ground? Can two things be true at once?",
        "patterns": [
            r"\b(always|never|every time|every single|nobody|everybody)\b",
            r"\b(nothing ever|everything always)\b",
            r"\b(completely|totally|absolutely|entirely) (worthless|useless|perfect|terrible)\b",
            r"\b(either .* or)\b",
            r"\b(100%|zero|0%) (right|wrong|good|bad|failure|success)\b",
            r"\b(if i can'?t .* then)\b.*\b(no point|give up|worthless|why bother)\b",
            r"\b(perfect or nothing|all or nothing)\b",
        ],
    },
    "mind_reading": {
        "label": "Mind Reading",
        "description": "Assuming you know what others think without evidence",
        "reframe": "What evidence do you actually have? Could there be other explanations?",
        "patterns": [
            r"\b(they|he|she|everyone) (thinks?|believes?|knows?) (i'?m|that i)\b.*\b(stupid|worthless|annoying|boring|failure)\b",
            r"\b(probably|definitely|obviously|clearly) (thinks?|hates?|judges?|doesn'?t (like|care|respect))\b",
            r"\b(they|people|everyone) (must|definitely) (think|feel|believe)\b",
            r"\bi (know|can tell|sense) (they|he|she|people) (think|feel|want)\b",
            r"\b(no one|nobody) (likes?|cares?|wants?|respects?)\b me\b",
            r"\bthey'?re (judging|laughing at|mocking|pitying)\b",
        ],
    },
    "fortune_telling": {
        "label": "Fortune Telling",
        "description": "Predicting negative outcomes as certain",
        "reframe": "Can you really predict the future? What other outcomes are possible?",
        "patterns": [
            r"\b(i know|i just know|guaranteed|definitely) .*(will|going to) .*(fail|go wrong|be terrible|not work)\b",
            r"\b(it'?s going to|this will) (be a disaster|fail|go wrong|end badly)\b",
            r"\b(there'?s no point|why bother)\b.*\b(because|since)\b.*\b(will|going to)\b",
            r"\b(i'?ll never|we'?ll never)\b.*\b(succeed|make it|be happy|find|get)\b",
            r"\bno matter what .*(won'?t|will never|can'?t)\b",
        ],
    },
    "emotional_reasoning": {
        "label": "Emotional Reasoning",
        "description": "Believing something is true because you feel it strongly",
        "reframe": "Feelings are real but not always facts. What does the evidence say?",
        "patterns": [
            r"\bi feel (like )?(a |i'?m a? )?(failure|loser|worthless|stupid|fraud)\b",
            r"\bi feel .* (so|therefore|which means) .*(i am|i must be|it'?s true)\b",
            r"\bbecause i feel .* (it must be|it is|that means)\b",
            r"\b(i feel|it feels) (hopeless|pointless|impossible)\b.*(so|therefore|meaning|which)\b",
            r"\bif i feel .* then .*(must be|is) true\b",
        ],
    },
    "should_statements": {
        "label": "Should Statements",
        "description": "Rigid rules about how you or others must behave",
        "reframe": "Who made this rule? Is this a preference or a genuine obligation?",
        "patterns": [
            r"\bi (should|shouldn'?t|must|have to|ought to|need to)\b.*\b(always|never|more|less|better)\b",
            r"\b(they|he|she|people) (should|shouldn'?t|must|ought to)\b",
            r"\bi (should have|shouldn'?t have|must have|ought to have)\b",
            r"\b(why can'?t i just|why don'?t i just)\b",
            r"\b(supposed to|expected to)\b.*\b(but|yet|however)\b",
        ],
    },
    "labeling": {
        "label": "Labeling",
        "description": "Attaching a fixed negative label to yourself or others",
        "reframe": "One action or quality doesn't define a whole person. What's more accurate?",
        "patterns": [
            r"\bi'?m (a |an |such a )?(idiot|loser|failure|fraud|mess|disaster|joke|burden|waste|wreck)\b",
            r"\bi'?m (so |too |completely |just )?(stupid|worthless|useless|pathetic|incompetent|broken|damaged)\b",
            r"\b(he|she|they)'?s? (a |an |such a )?(idiot|jerk|narcissist|terrible person|monster)\b",
            r"\bi will always be (a )?(failure|loser|alone|broken|damaged)\b",
            r"\bi'?m nothing\b",
        ],
    },
    "overgeneralization": {
        "label": "Overgeneralization",
        "description": "Drawing broad conclusions from a single event",
        "reframe": "Is this truly a pattern, or one instance? What are the exceptions?",
        "patterns": [
            r"\b(this always happens|it always|i always)\b",
            r"\b(nothing ever|everything always|every time)\b",
            r"\b(typical|of course|here we go again|same old)\b",
            r"\b(i never|they never|no one ever)\b.*\b(anything right|good enough)\b",
            r"\b(just my luck|story of my life)\b",
        ],
    },
    "personalization": {
        "label": "Personalization",
        "description": "Blaming yourself for things outside your control",
        "reframe": "What factors were truly in your control versus outside it?",
        "patterns": [
            r"\b(my fault|all my fault|i caused|because of me|i ruined|i messed up)\b",
            r"\b(if only i had|i should have (prevented|stopped|known))\b",
            r"\b(they .* because (of me|i))\b",
            r"\b(i'?m (the reason|to blame|responsible for))\b.*\b(everything|all of this|their)\b",
            r"\b(everyone'?s .* is my fault)\b",
        ],
    },
    "discounting_positives": {
        "label": "Discounting the Positive",
        "description": "Dismissing good things as unimportant or luck",
        "reframe": "What if you took this positive at face value? You might deserve more credit than you think.",
        "patterns": [
            r"\b(yeah but|but that doesn'?t count|that was just luck|anyone could)\b",
            r"\b(it doesn'?t matter|big deal|so what|whatever)\b.*\b(good|great|accomplished|achieved)\b",
            r"\b(they'?re just being (nice|polite|kind))\b",
            r"\b(it was nothing|no big deal|doesn'?t mean anything)\b",
            r"\b(fluked?|got lucky|just (lucky|chance|coincidence))\b",
        ],
    },
    "mental_filter": {
        "label": "Mental Filter",
        "description": "Focusing only on the negative while ignoring positives",
        "reframe": "What went well that you might be overlooking?",
        "patterns": [
            r"\b(the only thing|all i (can )?(see|think|notice|remember) is)\b.*\b(bad|wrong|negative|terrible)\b",
            r"\b(everything was .* (but|except))\b.*\b(one|that one|this one)\b",
            r"\b(ruined|tainted|spoiled|overshadowed)\b.*\b(everything|whole|entire)\b",
            r"\b(can'?t (stop|help) (thinking|focusing|dwelling) (about|on))\b.*\b(bad|wrong|mistake|negative)\b",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
#  CRISIS KEYWORDS & RESOURCES
# ══════════════════════════════════════════════════════════════════

CRISIS_KEYWORDS = [
    r"\b(want to|wanna|going to|gonna) (die|kill myself|end (it|my life|everything))\b",
    r"\b(suicid|kill myself|end my life|take my (own )?life)\b",
    r"\b(don'?t want to (live|be alive|exist|be here|wake up))\b",
    r"\b(better off dead|better off without me|world would be better)\b",
    r"\b(no reason to (live|go on|continue|keep going))\b",
    r"\b(planning to|plan to|decided to) .*(die|end it|kill)\b",
    r"\b(self[- ]?harm|cutting myself|hurt myself|hurting myself)\b",
    r"\b(overdose|pills|jump off|hang myself)\b",
    r"\b(final (goodbye|letter|note|message))\b",
    r"\b(can'?t (do this|take it|go on|keep going) anymore)\b",
    r"\b(everything would be better if i (was|were) (gone|dead))\b",
]

CRISIS_RESOURCES = """
---
**🆘 You matter. Please reach out for support:**

🇺🇸 **988 Suicide & Crisis Lifeline:** Call or text **988** (24/7)
🇺🇸 **Crisis Text Line:** Text **HOME** to **741741**
🌍 **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/
🌍 **Befrienders Worldwide:** https://befrienders.org/

💡 If you're in immediate danger, please call your local emergency number.

*You're not alone, and asking for help is a sign of strength.*

---
"""


# ══════════════════════════════════════════════════════════════════
#  BIG FIVE PERSONALITY TRAIT HINTS
# ══════════════════════════════════════════════════════════════════

BIG_FIVE_LEXICON = {
    "openness": {
        "high": [
            "creative", "curious", "imaginative", "artistic",
            "adventurous", "exploring", "philosophical", "abstract",
            "innovative", "unconventional", "experimental",
            "wonder", "discover", "invent", "dream", "imagine",
            "new idea", "try something new", "think outside",
        ],
        "low": [
            "practical", "routine", "traditional", "conventional",
            "predictable", "familiar", "same old", "comfortable with",
            "prefer not to change", "stick with",
        ],
    },
    "conscientiousness": {
        "high": [
            "organized", "disciplined", "responsible", "reliable",
            "punctual", "thorough", "diligent", "methodical",
            "plan", "schedule", "goal", "productive", "efficient",
            "on track", "to-do", "checklist", "prioritize",
        ],
        "low": [
            "procrastinate", "procrastinating", "lazy", "messy",
            "disorganized", "forgot", "late", "missed deadline",
            "put off", "can't focus", "scattered", "careless",
        ],
    },
    "extraversion": {
        "high": [
            "party", "friends", "social", "outgoing", "energetic",
            "talkative", "meeting people", "crowd", "gathering",
            "hung out", "went out", "fun night", "socializing",
            "networking", "team", "group activity",
        ],
        "low": [
            "alone time", "introvert", "solitude", "quiet",
            "stayed in", "by myself", "prefer alone",
            "too many people", "drained by", "need space",
            "recharge", "overwhelmed by crowds",
        ],
    },
    "agreeableness": {
        "high": [
            "kind", "helpful", "generous", "compassionate",
            "empathetic", "forgiving", "cooperative", "supportive",
            "volunteer", "charity", "helped someone", "listened to",
            "patient", "understanding", "trust",
        ],
        "low": [
            "competitive", "stubborn", "confrontation",
            "argument", "skeptical", "suspicious", "distrustful",
            "don't trust", "annoyed by people", "selfish",
        ],
    },
    "neuroticism": {
        "high": [
            "anxious", "worried", "nervous", "stressed",
            "insecure", "moody", "emotional", "overwhelmed",
            "overthinking", "ruminating", "catastrophizing",
            "can't relax", "restless", "tense", "on edge",
            "fragile", "sensitive", "reactive", "volatile",
        ],
        "low": [
            "calm", "relaxed", "stable", "resilient",
            "even-keeled", "unbothered", "at peace", "steady",
            "grounded", "centered", "composed", "unfazed",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
#  TOPIC & ENTITY LEXICONS
# ══════════════════════════════════════════════════════════════════

TOPIC_KEYWORDS = {
    "work": [
        "work", "job", "office", "career", "boss", "colleague",
        "meeting", "project", "deadline", "promotion", "salary",
        "coworker", "manager", "workplace", "corporate",
        "resign", "fired", "hired", "interview", "client",
        "presentation", "report", "overtime", "commute",
    ],
    "relationships": [
        "partner", "boyfriend", "girlfriend", "husband", "wife",
        "spouse", "relationship", "dating", "marriage", "divorce",
        "breakup", "love", "romantic", "ex", "crush",
        "together", "anniversary", "commitment", "intimacy",
    ],
    "family": [
        "family", "mother", "father", "mom", "dad", "parent",
        "sister", "brother", "sibling", "child", "children",
        "son", "daughter", "grandparent", "grandmother",
        "grandfather", "uncle", "aunt", "cousin", "in-law",
    ],
    "health": [
        "health", "doctor", "hospital", "sick", "illness",
        "medicine", "medication", "therapy", "therapist",
        "exercise", "workout", "diet", "sleep", "insomnia",
        "headache", "fatigue", "pain", "diagnosis", "symptom",
        "weight", "gym", "meditation", "yoga", "wellness",
    ],
    "finance": [
        "money", "financial", "finance", "budget", "debt",
        "loan", "saving", "savings", "expense", "income",
        "rent", "mortgage", "investment", "bills", "afford",
        "broke", "expensive", "cost", "paycheck", "bank",
    ],
    "education": [
        "school", "university", "college", "class", "study",
        "studying", "exam", "test", "grade", "assignment",
        "homework", "professor", "teacher", "lecture",
        "learning", "course", "degree", "thesis", "research",
    ],
    "social": [
        "friend", "friends", "friendship", "social",
        "hang out", "party", "gathering", "community",
        "group", "meet", "met", "people", "conversation",
        "lonely", "isolated", "belong", "fitting in",
    ],
    "self_growth": [
        "growth", "self-improvement", "goal", "habit",
        "mindfulness", "meditation", "journal", "reflection",
        "gratitude", "self-care", "boundaries", "healing",
        "progress", "change", "transform", "evolve",
        "self-awareness", "intention", "purpose", "meaning",
    ],
    "sleep": [
        "sleep", "sleeping", "slept", "insomnia", "nightmare",
        "nap", "rest", "resting", "bed", "bedtime",
        "wake up", "woke up", "tired", "well-rested",
        "oversleep", "can't sleep", "sleep quality",
    ],
    "creativity": [
        "creative", "art", "music", "writing", "painting",
        "drawing", "singing", "playing", "instrument",
        "poem", "story", "novel", "dance", "photography",
        "craft", "design", "inspired", "muse", "compose",
    ],
}

TIME_OF_DAY_PATTERNS = [
    ("morning", [
        "morning", "woke up", "wake up", "sunrise", "breakfast",
        "am", "dawn", "early",
    ]),
    ("afternoon", [
        "afternoon", "lunch", "midday", "noon", "pm",
    ]),
    ("evening", [
        "evening", "dinner", "sunset", "dusk", "pm",
    ]),
    ("night", [
        "night", "bedtime", "midnight", "late", "sleep",
        "insomnia", "dark",
    ]),
]

DAY_PATTERNS = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
    "weekend", "weekday", "workday",
]


# ══════════════════════════════════════════════════════════════════
#  CORE NLP FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def _tokenize(text):
    """Lowercase tokenisation with basic cleaning."""
    return re.findall(r"[a-z']+(?:-[a-z']+)*", text.lower())


def sentiment_score(text):
    """Return sentiment score in [-1, 1] using lexicon + negation + intensifiers."""
    tokens = _tokenize(text)
    if not tokens:
        return 0.0

    total = 0.0
    count = 0
    i = 0

    while i < len(tokens):
        token = tokens[i]

        # Check for negation
        is_negated = False
        if i > 0 and tokens[i - 1] in _NEGATION_WORDS:
            is_negated = True

        # Check for intensifier
        intensifier = 1.0
        if i > 0 and tokens[i - 1] in _INTENSIFIERS:
            intensifier = _INTENSIFIERS[tokens[i - 1]]
        if i > 1 and tokens[i - 2] in _INTENSIFIERS:
            intensifier = max(
                intensifier, _INTENSIFIERS[tokens[i - 2]]
            )

        # Lookup score
        score = 0.0
        if token in _POS_WORDS:
            score = _POS_WORDS[token]
        elif token in _NEG_WORDS:
            score = _NEG_WORDS[token]

        if score != 0.0:
            score *= intensifier
            if is_negated:
                score *= -0.75  # partial flip
            total += score
            count += 1

        i += 1

    if count == 0:
        return 0.0

    # Normalize to [-1, 1]
    raw = total / max(count, 1)
    return max(-1.0, min(1.0, raw / 4.0))


def detect_emotions(text):
    """Detect emotions with counts. Returns dict {emotion: count}."""
    tokens = set(_tokenize(text))
    text_lower = text.lower()
    result = {}

    for emotion, keywords in EMOTION_LEXICON.items():
        hits = 0
        for kw in keywords:
            if " " in kw:
                if kw in text_lower:
                    hits += 1
            elif kw in tokens:
                hits += 1
        if hits > 0:
            result[emotion] = hits

    return result if result else None


def detect_granular_emotions(text):
    """Detect sub-emotions for deeper granularity.
    Returns {parent: {sub_emotion: count}}."""
    tokens = set(_tokenize(text))
    text_lower = text.lower()
    result = {}

    for parent, subs in EMOTION_GRANULARITY.items():
        sub_hits = {}
        for sub_name, keywords in subs.items():
            hits = 0
            for kw in keywords:
                if " " in kw:
                    if kw in text_lower:
                        hits += 1
                elif kw in tokens:
                    hits += 1
            if hits > 0:
                sub_hits[sub_name] = hits
        if sub_hits:
            result[parent] = sub_hits

    return result if result else None


def detect_cognitive_distortions(text):
    """Detect cognitive distortion patterns in text.
    Returns list of {type, label, description, reframe, matched}."""
    text_lower = text.lower()
    found = []

    for dist_type, dist_info in COGNITIVE_DISTORTIONS.items():
        for pattern in dist_info["patterns"]:
            try:
                match = re.search(pattern, text_lower)
                if match:
                    found.append({
                        "type": dist_type,
                        "label": dist_info["label"],
                        "description": dist_info["description"],
                        "reframe": dist_info["reframe"],
                        "matched": match.group(0),
                    })
                    break  # one match per distortion type
            except re.error:
                continue

    return found if found else None


def detect_crisis(text):
    """Check for crisis/self-harm language. Returns bool."""
    text_lower = text.lower()
    for pattern in CRISIS_KEYWORDS:
        try:
            if re.search(pattern, text_lower):
                return True
        except re.error:
            continue
    return False


def extract_entities(text):
    """Extract named entities (people) using capitalization heuristics."""
    # Find capitalised words that aren't sentence starters
    sentences = re.split(r'[.!?]+', text)
    people = Counter()
    skip = {
        "I", "The", "A", "An", "This", "That", "My", "We",
        "They", "It", "He", "She", "You", "But", "And",
        "So", "When", "What", "How", "Why", "Where",
        "Today", "Yesterday", "Tomorrow", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November",
        "December", "Also", "However", "Then", "After",
        "Before", "During", "Still", "Just", "Maybe",
        "Sometimes", "Perhaps", "Already", "Finally",
        "MindMirror", "God", "AI",
    }
    for sent in sentences:
        words = sent.strip().split()
        for i, word in enumerate(words):
            clean = re.sub(r"[^A-Za-z']", "", word)
            if (
                clean
                and clean[0].isupper()
                and clean not in skip
                and len(clean) > 1
                and i > 0  # skip sentence starters
            ):
                people[clean] += 1

    return people.most_common(15)


def extract_topics(text):
    """Extract topics with occurrence counts."""
    tokens = set(_tokenize(text))
    text_lower = text.lower()
    result = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        hits = 0
        for kw in keywords:
            if " " in kw:
                if kw in text_lower:
                    hits += 1
            elif kw in tokens:
                hits += 1
        if hits > 0:
            result[topic] = hits

    return result


def word_frequencies(text, top_n=30):
    """Return top-N word frequencies, excluding stopwords."""
    stop = {
        "i", "me", "my", "myself", "we", "our", "ours",
        "you", "your", "yours", "he", "him", "his",
        "she", "her", "hers", "it", "its", "they", "them",
        "their", "theirs", "what", "which", "who", "whom",
        "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has",
        "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "if", "or",
        "because", "as", "until", "while", "of", "at",
        "by", "for", "with", "about", "against", "between",
        "through", "during", "before", "after", "above",
        "below", "to", "from", "up", "down", "in", "out",
        "on", "off", "over", "under", "again", "further",
        "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very",
        "s", "t", "can", "will", "just", "don", "should",
        "now", "d", "ll", "m", "o", "re", "ve", "y",
        "ain", "aren", "couldn", "didn", "doesn", "hadn",
        "hasn", "haven", "isn", "ma", "mightn", "mustn",
        "needn", "shan", "shouldn", "wasn", "weren",
        "won", "wouldn", "also", "really", "would", "could",
        "like", "much", "even", "still", "well", "back",
        "going", "went", "got", "get", "make", "made",
        "thing", "things", "know", "think", "feel",
        "today", "day", "time", "way", "lot",
    }
    tokens = _tokenize(text)
    filtered = [
        t for t in tokens
        if t not in stop and len(t) > 2
    ]
    return Counter(filtered).most_common(top_n)


def detect_time_of_day(text):
    """Detect time-of-day mentions."""
    tokens = set(_tokenize(text))
    text_lower = text.lower()
    result = Counter()
    for period, keywords in TIME_OF_DAY_PATTERNS:
        for kw in keywords:
            if " " in kw:
                if kw in text_lower:
                    result[period] += 1
            elif kw in tokens:
                result[period] += 1
    return result.most_common()


def detect_day_mentions(text):
    """Detect day-of-week mentions."""
    text_lower = text.lower()
    result = Counter()
    for day in DAY_PATTERNS:
        count = len(re.findall(r'\b' + day + r'\b', text_lower))
        if count:
            result[day.title()] = count
    return result.most_common()


# ══════════════════════════════════════════════════════════════════
#  BIG FIVE ESTIMATION
# ══════════════════════════════════════════════════════════════════

def estimate_big_five(text):
    """Estimate Big Five trait tendencies from text.
    Returns dict with scores in [-1, 1] (negative = low trait)."""
    tokens = set(_tokenize(text))
    text_lower = text.lower()
    scores = {}

    for trait, poles in BIG_FIVE_LEXICON.items():
        high_hits = 0
        low_hits = 0
        for kw in poles["high"]:
            if " " in kw:
                if kw in text_lower:
                    high_hits += 1
            elif kw in tokens:
                high_hits += 1
        for kw in poles["low"]:
            if " " in kw:
                if kw in text_lower:
                    low_hits += 1
            elif kw in tokens:
                low_hits += 1
        total = high_hits + low_hits
        if total > 0:
            scores[trait] = (high_hits - low_hits) / total
        else:
            scores[trait] = 0.0

    return scores


# ══════════════════════════════════════════════════════════════════
#  GROWTH METRIC CALCULATIONS
# ══════════════════════════════════════════════════════════════════

def calculate_emotional_regulation(entries):
    """Score emotional regulation based on sentiment volatility.
    Lower volatility = better regulation. Returns 0-100 score."""
    sentiments = [
        e.get("sentiment", 0)
        for e in entries
        if e.get("sentiment") is not None
    ]
    if len(sentiments) < 3:
        return None

    # Calculate volatility as average absolute diff
    diffs = [
        abs(sentiments[i] - sentiments[i - 1])
        for i in range(1, len(sentiments))
    ]
    avg_volatility = sum(diffs) / len(diffs)

    # Map to 0-100 (lower volatility = higher score)
    # avg_volatility of 0 → 100, avg_volatility of 1 → 0
    score = max(0, min(100, (1 - avg_volatility) * 100))
    return round(score, 1)


def calculate_resilience(entries):
    """Score resilience based on recovery patterns after negative entries.
    Returns 0-100 score."""
    sentiments = [
        e.get("sentiment", 0)
        for e in entries
        if e.get("sentiment") is not None
    ]
    if len(sentiments) < 5:
        return None

    recoveries = 0
    dips = 0

    for i in range(1, len(sentiments) - 1):
        if sentiments[i] < -0.2:  # negative entry
            dips += 1
            # Check next 1-2 entries for recovery
            future = sentiments[i + 1: i + 3]
            if any(s > sentiments[i] + 0.2 for s in future):
                recoveries += 1

    if dips == 0:
        return 85.0  # no dips = stable (not perfect since untested)

    score = (recoveries / dips) * 100
    return round(min(100, score), 1)


def calculate_self_awareness(entries):
    """Score self-awareness based on emotional vocabulary diversity
    and pattern recognition indicators. Returns 0-100."""
    if len(entries) < 3:
        return None

    all_emotions = set()
    reflection_keywords = {
        "realize", "realized", "notice", "noticed", "aware",
        "awareness", "understand", "understood", "recognize",
        "recognized", "pattern", "trigger", "insight",
        "learned", "learning", "growth", "reflect",
        "reflecting", "reflection", "mindful", "conscious",
    }

    reflection_count = 0
    total_entries = len(entries)

    for e in entries:
        content = e.get("content", "")
        tokens = set(_tokenize(content))

        # Emotion diversity
        for emotion, keywords in EMOTION_LEXICON.items():
            if any(kw in tokens for kw in keywords):
                all_emotions.add(emotion)

        # Reflection indicators
        if tokens & reflection_keywords:
            reflection_count += 1

    # Combine diversity and reflection
    diversity_score = min(100, len(all_emotions) * 12)
    reflection_score = min(100, (reflection_count / total_entries) * 200)

    score = diversity_score * 0.5 + reflection_score * 0.5
    return round(min(100, score), 1)


def calculate_growth_metrics(entries):
    """Calculate all three growth metrics.
    Returns dict with scores and details."""
    if not entries or len(entries) < 3:
        return None

    # Use chronological order
    chronological = list(reversed(entries)) if entries else []

    regulation = calculate_emotional_regulation(chronological)
    resilience = calculate_resilience(chronological)
    awareness = calculate_self_awareness(chronological)

    # Also calculate for first half vs second half (before/after)
    mid = len(chronological) // 2
    if mid >= 3:
        first_half = chronological[:mid]
        second_half = chronological[mid:]
        reg_before = calculate_emotional_regulation(first_half)
        reg_after = calculate_emotional_regulation(second_half)
        res_before = calculate_resilience(first_half)
        res_after = calculate_resilience(second_half)
        awa_before = calculate_self_awareness(first_half)
        awa_after = calculate_self_awareness(second_half)
    else:
        reg_before = reg_after = None
        res_before = res_after = None
        awa_before = awa_after = None

    return {
        "emotional_regulation": regulation,
        "resilience": resilience,
        "self_awareness": awareness,
        "before_after": {
            "regulation": {"before": reg_before, "after": reg_after},
            "resilience": {"before": res_before, "after": res_after},
            "awareness": {"before": awa_before, "after": awa_after},
        },
    }


# ══════════════════════════════════════════════════════════════════
#  PREDICTIVE SUPPORT HELPERS
# ══════════════════════════════════════════════════════════════════

def detect_mood_trend(sentiments, window=5):
    """Detect if mood is trending up, down, or stable.
    Input: list of {date, score} dicts sorted chronologically.
    Returns: trend string and slope value."""
    if len(sentiments) < window:
        return "insufficient_data", 0.0

    recent = [s["score"] for s in sentiments[-window:]]
    older = [s["score"] for s in sentiments[-(window * 2):-window]]

    if not older:
        return "insufficient_data", 0.0

    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)
    diff = recent_avg - older_avg

    if diff > 0.15:
        return "improving", diff
    elif diff < -0.15:
        return "declining", diff
    else:
        return "stable", diff


def find_triggers(entries, threshold=-0.2):
    """Find topics that correlate with negative sentiment.
    Returns list of (topic, avg_sentiment, count)."""
    topic_sentiments = defaultdict(list)

    for e in entries:
        sent = e.get("sentiment")
        tags_raw = e.get("tags")
        if sent is None or tags_raw is None:
            continue
        try:
            tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(tags, list):
            for tag in tags:
                topic_sentiments[tag].append(sent)

    triggers = []
    for topic, sents in topic_sentiments.items():
        if len(sents) >= 2:
            avg = sum(sents) / len(sents)
            if avg < threshold:
                triggers.append((topic, round(avg, 3), len(sents)))

    triggers.sort(key=lambda x: x[1])
    return triggers


def detect_day_of_week_patterns(entries):
    """Find which days of the week tend to have lower/higher mood.
    Returns dict {day_name: avg_sentiment}."""
    day_sents = defaultdict(list)

    for e in entries:
        date_str = e.get("entry_date", "")[:10]
        sent = e.get("sentiment")
        if not date_str or sent is None:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = dt.strftime("%A")
            day_sents[day_name].append(sent)
        except ValueError:
            continue

    result = {}
    for day, sents in day_sents.items():
        if sents:
            result[day] = round(sum(sents) / len(sents), 3)

    return result


def detect_surprise_patterns(entries, window=10):
    """Detect when recent entries break the user's normal patterns.
    Returns list of surprise descriptions."""
    if len(entries) < window + 1:
        return []

    surprises = []
    # Calculate baseline from older entries
    older = entries[1:window + 1]  # entries are newest-first
    baseline_sents = [
        e.get("sentiment", 0) for e in older
        if e.get("sentiment") is not None
    ]
    if not baseline_sents:
        return []

    baseline_avg = sum(baseline_sents) / len(baseline_sents)
    baseline_std = (
        sum((s - baseline_avg) ** 2 for s in baseline_sents)
        / len(baseline_sents)
    ) ** 0.5

    # Check most recent entry
    latest = entries[0]
    latest_sent = latest.get("sentiment")
    if latest_sent is not None and baseline_std > 0:
        z_score = (latest_sent - baseline_avg) / max(baseline_std, 0.1)

        if z_score > 1.5:
            date_str = latest.get("entry_date", "")[:10]
            surprises.append(
                f"You felt unexpectedly positive on {date_str} "
                f"(sentiment {latest_sent:+.2f} vs your average "
                f"{baseline_avg:+.2f}). What changed? 🌟"
            )
        elif z_score < -1.5:
            date_str = latest.get("entry_date", "")[:10]
            surprises.append(
                f"Your mood dipped noticeably on {date_str} "
                f"(sentiment {latest_sent:+.2f} vs your average "
                f"{baseline_avg:+.2f}). Something weighing on you? 💙"
            )

    # Check for broken streaks (e.g., a usually negative topic
    # appearing with positive sentiment)
    # (kept simple for now)

    return surprises


def generate_dynamic_prompts(entries, goals=None):
    """Generate personalised journaling prompts based on recent patterns.
    Returns list of prompt strings."""
    prompts = []

    if not entries:
        return [
            "What brought you the most peace today?",
            "Describe one small thing that made you smile recently.",
            "What's something you're looking forward to?",
        ]

    # Analyse recent entries
    recent = entries[:5]
    all_emotions = Counter()
    all_topics = Counter()

    for e in recent:
        content = e.get("content", "")
        emos = detect_emotions(content)
        if emos:
            all_emotions.update(emos)
        topics = extract_topics(content)
        if topics:
            all_topics.update(topics)

    # Recent sentiment
    recent_sents = [
        e.get("sentiment", 0) for e in recent
        if e.get("sentiment") is not None
    ]
    avg_sent = sum(recent_sents) / len(recent_sents) if recent_sents else 0

    # Generate based on patterns
    if avg_sent < -0.2:
        prompts.extend([
            "What's one thing you can do right now to be gentle with yourself?",
            "Write about a time you overcame something difficult. What strengths did you use?",
            "What would you say to a friend feeling the way you do?",
        ])
    elif avg_sent > 0.2:
        prompts.extend([
            "What's fueling your positive energy lately? How can you protect it?",
            "Describe the best moment of your recent days in vivid detail.",
            "What's a goal that feels exciting and achievable right now?",
        ])
    else:
        prompts.extend([
            "What are you noticing about yourself this week?",
            "What's something you'd like to change, even slightly?",
        ])

    # Topic-specific prompts
    top_topics = all_topics.most_common(2)
    topic_prompts = {
        "work": "How is your work affecting your energy and mood? What boundaries might help?",
        "relationships": "What do you need most from your close relationships right now?",
        "health": "How has your body been feeling? What's one healthy habit you'd like to strengthen?",
        "sleep": "Describe your sleep patterns lately. What helps you rest well?",
        "family": "What's one thing you appreciate about your family? What's one tension you'd like to ease?",
        "self_growth": "What growth have you noticed in yourself recently, even small changes?",
        "finance": "What's your relationship with money feeling like? Any worries or wins?",
        "social": "How connected do you feel to others this week? What would help?",
    }
    for topic, _ in top_topics:
        if topic in topic_prompts:
            prompts.append(topic_prompts[topic])

    # Emotion-specific prompts
    top_emos = all_emotions.most_common(2)
    emo_prompts = {
        "fear": "What feels most uncertain right now? What's within your control?",
        "anger": "What's frustrating you? Underneath the anger, what need isn't being met?",
        "shame": "When you feel shame, what belief about yourself drives it? Is it fair?",
        "exhaustion": "What's draining your energy most? What could you say 'no' to?",
        "confusion": "What's one question that, if answered, would bring you clarity?",
    }
    for emo, _ in top_emos:
        if emo in emo_prompts:
            prompts.append(emo_prompts[emo])

    # Goal-related prompts
    if goals:
        active = [g for g in goals if g.get("status") == "active"]
        if active:
            prompts.append(
                f"How are you feeling about your goal: \"{active[0].get('goal_text', '')}\"? "
                f"What's one small step you can take today?"
            )

    return prompts[:6]  # max 6 prompts


# ══════════════════════════════════════════════════════════════════
#  WELLBEING SCREENING HELPERS (non-diagnostic)
# ══════════════════════════════════════════════════════════════════

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure",
    "Trouble concentrating on things",
    "Moving or speaking slowly, or being fidgety/restless",
    "Thoughts that you would be better off dead, or of hurting yourself",
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen",
]

SCREENING_OPTIONS = {
    0: "Not at all",
    1: "Several days",
    2: "More than half the days",
    3: "Nearly every day",
}


def interpret_phq9(total):
    """Non-diagnostic PHQ-9 interpretation."""
    if total <= 4:
        return "minimal", "Your responses suggest minimal depressive symptoms. Keep nurturing your wellbeing! 🌿"
    elif total <= 9:
        return "mild", "Your responses suggest mild depressive symptoms. Self-care practices and journaling can help. Consider talking to someone you trust. 💙"
    elif total <= 14:
        return "moderate", "Your responses suggest moderate depressive symptoms. It may be helpful to speak with a mental health professional for support. 🤝"
    elif total <= 19:
        return "moderately severe", "Your responses suggest moderately severe symptoms. Reaching out to a mental health professional is recommended. You don't have to face this alone. 💛"
    else:
        return "severe", "Your responses suggest severe symptoms. Please consider reaching out to a mental health professional or crisis resource soon. You deserve support. 🆘"


def interpret_gad7(total):
    """Non-diagnostic GAD-7 interpretation."""
    if total <= 4:
        return "minimal", "Your responses suggest minimal anxiety symptoms. Keep up your coping strategies! 🌿"
    elif total <= 9:
        return "mild", "Your responses suggest mild anxiety. Mindfulness and grounding exercises may help. 💙"
    elif total <= 14:
        return "moderate", "Your responses suggest moderate anxiety. Speaking with a professional could provide valuable support. 🤝"
    else:
        return "severe", "Your responses suggest severe anxiety symptoms. Reaching out to a mental health professional is recommended. 💛"


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 2 — paste Chunk 3 (analyzer.py Part 2) below this
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — analyzer.py  PART 2 of 2  (v3 · Enhanced)     ║
# ║  CHUNK 3 of 10                                                  ║
# ║  local_analysis, emotion networks, topic-sentiment correlation, ║
# ║  AI analysis, AI chat (therapeutic modes, crisis protocol,      ║
# ║  empathy calibration), reflection prompts, session summaries,   ║
# ║  narrative summaries, mood forecasting                          ║
# ╚══════════════════════════════════════════════════════════════════╝

from google import genai
from google.genai import types


# ══════════════════════════════════════════════════════════════════
#  EMOTION CO-OCCURRENCE NETWORK
# ══════════════════════════════════════════════════════════════════

def build_emotion_network(entries):
    """Build emotion co-occurrence data for network graph.
    Returns {nodes: [{id, count}], edges: [{source, target, weight}]}."""
    emotion_counts = Counter()
    co_occurrence = Counter()

    for e in entries:
        content = e.get("content", "")
        emos = detect_emotions(content)
        if not emos:
            continue

        emo_list = list(emos.keys())
        for emo in emo_list:
            emotion_counts[emo] += emos[emo]

        # Pairwise co-occurrence
        for i in range(len(emo_list)):
            for j in range(i + 1, len(emo_list)):
                pair = tuple(sorted([emo_list[i], emo_list[j]]))
                co_occurrence[pair] += 1

    if not emotion_counts:
        return None

    nodes = [
        {"id": emo, "count": cnt}
        for emo, cnt in emotion_counts.most_common()
    ]
    edges = [
        {"source": pair[0], "target": pair[1], "weight": cnt}
        for pair, cnt in co_occurrence.most_common()
        if cnt >= 1
    ]

    return {"nodes": nodes, "edges": edges}


# ══════════════════════════════════════════════════════════════════
#  TOPIC-SENTIMENT CORRELATION
# ══════════════════════════════════════════════════════════════════

def compute_topic_sentiment_correlation(entries):
    """Compute average sentiment per topic for outcome linking.
    Returns dict {topic: {avg_sentiment, count, trend_word}}."""
    topic_data = defaultdict(list)

    for e in entries:
        content = e.get("content", "")
        sent = e.get("sentiment")
        if sent is None:
            sent = sentiment_score(content)

        topics = extract_topics(content)
        for topic in topics:
            topic_data[topic].append(sent)

    result = {}
    for topic, sents in topic_data.items():
        if len(sents) >= 2:
            avg = sum(sents) / len(sents)
            if avg > 0.15:
                trend = "positive"
            elif avg < -0.15:
                trend = "negative"
            else:
                trend = "neutral"
            result[topic] = {
                "avg_sentiment": round(avg, 3),
                "count": len(sents),
                "trend": trend,
            }

    return result


# ══════════════════════════════════════════════════════════════════
#  SEASONALITY & WEEKLY HEATMAP DATA
# ══════════════════════════════════════════════════════════════════

def compute_weekly_heatmap(entries):
    """Build a weekday × hour heatmap of average sentiment.
    Returns list of {day, hour, avg_sentiment, count}."""
    grid = defaultdict(list)

    for e in entries:
        date_str = e.get("entry_date", "")
        sent = e.get("sentiment")
        if not date_str or sent is None:
            continue
        try:
            dt = datetime.strptime(date_str[:16], "%Y-%m-%d %H:%M")
            day = dt.strftime("%A")
            hour = dt.hour
            grid[(day, hour)].append(sent)
        except ValueError:
            try:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                day = dt.strftime("%A")
                grid[(day, 12)].append(sent)
            except ValueError:
                continue

    result = []
    for (day, hour), sents in grid.items():
        result.append({
            "day": day,
            "hour": hour,
            "avg_sentiment": round(sum(sents) / len(sents), 3),
            "count": len(sents),
        })

    return result


# ══════════════════════════════════════════════════════════════════
#  COGNITIVE DISTORTION AGGREGATION
# ══════════════════════════════════════════════════════════════════

def aggregate_distortions(entries):
    """Aggregate cognitive distortions across entries.
    Returns {distortion_type: {count, label, description, reframe,
    examples: [matched_text]}}."""
    agg = {}

    for e in entries:
        content = e.get("content", "")
        distortions = detect_cognitive_distortions(content)
        if not distortions:
            continue
        for d in distortions:
            dtype = d["type"]
            if dtype not in agg:
                agg[dtype] = {
                    "count": 0,
                    "label": d["label"],
                    "description": d["description"],
                    "reframe": d["reframe"],
                    "examples": [],
                }
            agg[dtype]["count"] += 1
            if len(agg[dtype]["examples"]) < 3:
                agg[dtype]["examples"].append(d["matched"])

    return agg


# ══════════════════════════════════════════════════════════════════
#  ENHANCED LOCAL ANALYSIS
# ══════════════════════════════════════════════════════════════════

def local_analysis(entries):
    """Comprehensive local pattern analysis on a list of entries
    (chronological order expected, oldest first).
    Returns a rich analysis dict."""
    if not entries:
        return None

    # ── Basics ───────────────────────────────────────────────────
    all_text = " ".join(e.get("content", "") for e in entries)

    sentiments = []
    emotions_agg = defaultdict(list)
    granular_agg = defaultdict(lambda: defaultdict(int))
    topics_agg = Counter()
    distortion_entries = []
    mood_scores = []
    energy_scores = []

    for e in entries:
        content = e.get("content", "")
        date = e.get("entry_date", "")

        # Sentiment
        sent = e.get("sentiment")
        if sent is None:
            sent = sentiment_score(content)
        sentiments.append({"date": date, "score": sent})

        # Mood and energy
        ms = e.get("mood_score")
        if ms is not None:
            mood_scores.append({"date": date, "score": ms})
        el = e.get("energy_level")
        if el is not None:
            energy_scores.append({"date": date, "score": el})

        # Emotions
        emos = detect_emotions(content)
        if emos:
            for emo, cnt in emos.items():
                emotions_agg[emo].append(date)

        # Granular emotions
        gran = detect_granular_emotions(content)
        if gran:
            for parent, subs in gran.items():
                for sub, cnt in subs.items():
                    granular_agg[parent][sub] += cnt

        # Topics
        topics = extract_topics(content)
        topics_agg.update(topics)

        # Distortions
        dists = detect_cognitive_distortions(content)
        if dists:
            distortion_entries.append({
                "date": date,
                "distortions": dists,
            })

    # ── Aggregate calculations ───────────────────────────────────
    all_sents = [s["score"] for s in sentiments]
    avg_sent = sum(all_sents) / len(all_sents) if all_sents else 0

    # Emotion diversity
    emotion_diversity = len(emotions_agg)

    # People & words
    people = extract_entities(all_text)
    words = word_frequencies(all_text)

    # Time / day patterns
    times = detect_time_of_day(all_text)
    days = detect_day_mentions(all_text)

    # Big Five
    big_five = estimate_big_five(all_text)

    # Growth metrics
    growth = calculate_growth_metrics(entries)

    # Distortion aggregation
    distortions_summary = aggregate_distortions(entries)

    # Emotion network
    emotion_network = build_emotion_network(entries)

    # Topic-sentiment correlation
    topic_sentiment = compute_topic_sentiment_correlation(entries)

    # Mood trend
    trend_label, trend_slope = detect_mood_trend(sentiments)

    # Day-of-week patterns
    dow_patterns = detect_day_of_week_patterns(entries)

    # Triggers
    triggers = find_triggers(entries)

    # Weekly heatmap
    weekly_heatmap = compute_weekly_heatmap(entries)

    # Surprises
    # (need newest-first for this function)
    surprises = detect_surprise_patterns(list(reversed(entries)))

    return {
        "entry_count": len(entries),
        "avg_sentiment": round(avg_sent, 3),
        "sentiments": sentiments,
        "mood_scores": mood_scores,
        "energy_scores": energy_scores,
        "emotions": dict(emotions_agg),
        "granular_emotions": {
            k: dict(v) for k, v in granular_agg.items()
        },
        "emotion_diversity": emotion_diversity,
        "topics": dict(topics_agg.most_common(20)),
        "people": people,
        "words": words,
        "times": times,
        "days": days,
        "big_five": big_five,
        "growth_metrics": growth,
        "distortions": distortions_summary,
        "distortion_entries": distortion_entries,
        "emotion_network": emotion_network,
        "topic_sentiment": topic_sentiment,
        "mood_trend": {"label": trend_label, "slope": trend_slope},
        "day_of_week_patterns": dow_patterns,
        "triggers": triggers,
        "weekly_heatmap": weekly_heatmap,
        "surprises": surprises,
    }


# ══════════════════════════════════════════════════════════════════
#  GEMINI HELPERS
# ══════════════════════════════════════════════════════════════════

def _call_gemini(prompt, api_key, model="gemini-2.5-flash",
                 temperature=0.7, max_tokens=4096):
    """Safely call Gemini and return text or error string."""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
    except Exception as exc:
        return f"⚠️ AI error: {exc}"


# ══════════════════════════════════════════════════════════════════
#  CONSENT NOTICE TEXT
# ══════════════════════════════════════════════════════════════════

CONSENT_NOTICE_ANALYSIS = (
    "📋 **Privacy:** Your writing is sent to Google Gemini for analysis. "
    "Nothing is stored afterward."
)

CONSENT_NOTICE_CHAT = (
    "📋 **Privacy:** Your message and recent journal context are processed "
    "by Google Gemini. Nothing persists after the conversation ends."
)


# ══════════════════════════════════════════════════════════════════
#  AI DEEP ANALYSIS
# ══════════════════════════════════════════════════════════════════

def ai_analysis(entries, api_key, model="gemini-2.5-flash",
                local_data=None, psyche_profile=None, goals=None):
    """Run comprehensive AI analysis using Gemini."""

    # Build entry summaries
    entry_block = "\n\n".join(
        f"[{e.get('entry_date', 'unknown')}] "
        f"(sentiment: {e.get('sentiment', 'N/A')}) "
        f"{e.get('content', '')[:500]}"
        for e in entries[:30]
    )

    # Build local data summary
    local_summary = ""
    if local_data:
        local_summary += f"\n\nLocal analysis summary:"
        local_summary += f"\n- Entries analyzed: {local_data.get('entry_count', 0)}"
        local_summary += f"\n- Average sentiment: {local_data.get('avg_sentiment', 0):+.3f}"
        local_summary += f"\n- Mood trend: {local_data.get('mood_trend', {}).get('label', 'unknown')}"
        local_summary += f"\n- Emotion diversity: {local_data.get('emotion_diversity', 0)} types"

        if local_data.get("topics"):
            top_topics = list(local_data["topics"].items())[:8]
            local_summary += f"\n- Top topics: {', '.join(f'{t}({c})' for t, c in top_topics)}"

        if local_data.get("distortions"):
            dist_list = [
                f"{d['label']}({d['count']})"
                for d in local_data["distortions"].values()
            ]
            local_summary += f"\n- Cognitive distortions detected: {', '.join(dist_list)}"

        if local_data.get("triggers"):
            trig_list = [f"{t[0]} (avg sent: {t[1]:+.2f})" for t in local_data["triggers"][:5]]
            local_summary += f"\n- Potential triggers: {', '.join(trig_list)}"

        if local_data.get("growth_metrics"):
            gm = local_data["growth_metrics"]
            if gm.get("emotional_regulation") is not None:
                local_summary += f"\n- Emotional regulation score: {gm['emotional_regulation']}/100"
            if gm.get("resilience") is not None:
                local_summary += f"\n- Resilience score: {gm['resilience']}/100"
            if gm.get("self_awareness") is not None:
                local_summary += f"\n- Self-awareness score: {gm['self_awareness']}/100"

        if local_data.get("big_five"):
            bf = local_data["big_five"]
            bf_str = ", ".join(f"{k}: {v:+.2f}" for k, v in bf.items() if v != 0)
            if bf_str:
                local_summary += f"\n- Big Five hints: {bf_str}"

        if local_data.get("topic_sentiment"):
            ts = local_data["topic_sentiment"]
            ts_str = ", ".join(
                f"{t}: {d['avg_sentiment']:+.2f} ({d['trend']})"
                for t, d in list(ts.items())[:6]
            )
            if ts_str:
                local_summary += f"\n- Topic-mood correlations: {ts_str}"

        if local_data.get("day_of_week_patterns"):
            dow = local_data["day_of_week_patterns"]
            worst = min(dow.items(), key=lambda x: x[1]) if dow else None
            best = max(dow.items(), key=lambda x: x[1]) if dow else None
            if worst and best:
                local_summary += (
                    f"\n- Day patterns: Best day = {best[0]} ({best[1]:+.2f}), "
                    f"Hardest day = {worst[0]} ({worst[1]:+.2f})"
                )

    # Profile context
    profile_context = ""
    if psyche_profile:
        profile_context = f"\n\nUser psyche profile: {json.dumps(psyche_profile)}"

    # Goals context
    goals_context = ""
    if goals:
        active_goals = [g for g in goals if g.get("status") == "active"]
        if active_goals:
            goals_list = ", ".join(g.get("title", "") for g in active_goals[:5])
            goals_context = f"\n\nUSER'S ACTIVE GOALS: {goals_list}"

    prompt = f"""You are an incisive observer who has studied this person's journal entries 
with care and precision. You combine deep emotional intelligence with clarity of thought.

Write with confidence and warmth. Be direct, precise, and say more with fewer words. 
Respect the reader's intelligence. No filler, no platitudes, no therapy-speak.

{profile_context}
{goals_context}

JOURNAL ENTRIES:
{entry_block}
{local_summary}

YOUR REPORT SHOULD COVER:

1. **Emotional landscape** - What emotions dominate? What is absent or suppressed? 
   Map the full range with precision.

2. **Cognitive patterns** - Identify thinking traps (catastrophizing, black-and-white 
   reasoning, mind reading) with specific examples. Offer sharper alternatives.

3. **Recurring dynamics** - What cycles repeat? When do conditions improve or 
   deteriorate? Include temporal patterns and topic correlations.

4. **Growth trajectory** - Emotional regulation, resilience, and self-awareness 
   over time. Name the progress precisely, however incremental.

5. **What is ahead** - Based on trajectories, what is likely coming? What would 
   make the difference?

6. **Relational patterns** - How do connections and social dynamics surface in 
   these entries?

7. **What is already working** - Name the strategies, strengths, and supports 
   that are actively helping. Reinforce them.

8. **Recommendations** - 3-5 specific, actionable suggestions rooted in their 
   actual patterns. Include at least one embodied practice.

9. **The arc** - A brief narrative of their emotional trajectory, written directly 
   to them ("You have been..."). End with something honest and grounding.

VOICE:
- Confident and warm, never judgmental
- Precise language, no jargon or filler
- Honest and compassionate in equal measure
- Reference specific entries as evidence
- Use emoji sparingly (1-2 max)
- If crisis indicators appear, include support resources clearly
- Frame observations as patterns worth examining, not diagnoses
- Acknowledge limitations of the data
- If active goals are listed above, connect journal patterns to those goals

Write an insightful, precise report."""

    return _call_gemini(prompt, api_key, model, temperature=0.6, max_tokens=6000)


# ══════════════════════════════════════════════════════════════════
#  AI CHAT — THERAPEUTIC MODES & CRISIS PROTOCOL
# ══════════════════════════════════════════════════════════════════

CHAT_MODE_PROMPTS = {
    "open": {
        "label": "💬 Open Conversation",
        "system": (
            "You are MindMirror AI. You are an articulate, emotionally intelligent "
            "companion. Listen with precision, reflect what you observe, ask questions "
            "that open new angles, and share insight when it serves them. You are not "
            "a therapist. You are someone with genuine depth who pays close attention "
            "and communicates with clarity and care."
        ),
    },
    "cbt": {
        "label": "🧠 CBT Coaching",
        "system": (
            "You are MindMirror AI in cognitive coaching mode. Help them examine "
            "their thinking with precision. Identify distortions (catastrophizing, "
            "all-or-nothing reasoning, mind reading), test assumptions against "
            "evidence, and guide toward more accurate perspectives. Be transparent "
            "about the process: name what you are doing and why. Structured yet "
            "warm. Frame this as collaborative inquiry, not clinical intervention."
        ),
    },
    "validation": {
        "label": "💚 Validation Mode",
        "system": (
            "You are MindMirror AI in validation mode. Your role is to make them "
            "feel deeply understood. Reflect their emotions with nuance and accuracy. "
            "Affirm the logic of their feelings without rushing to solutions. "
            "Be present, steady, and precise in your empathy. Offer perspective "
            "only when invited."
        ),
    },
    "reflection": {
        "label": "🪞 Reflective Listening",
        "system": (
            "You are MindMirror AI in reflective mode. Mirror their words and "
            "emotional undertones with clarity. Ask questions that catalyze "
            "self-discovery rather than offering answers. Help them think: "
            "'What is really at stake here?' 'What would shift if that were true?' "
            "'What does this tell you about what you need?' Trust their capacity "
            "to find their own answers."
        ),
    },
    "homework": {
        "label": "📋 Check-in",
        "system": (
            "You are MindMirror AI in accountability mode. Help them assess "
            "progress on their goals and commitments with honesty and specificity. "
            "Acknowledge what is working, examine what is not, and help clarify "
            "next steps. Reference their journal patterns when relevant. "
            "Be encouraging and precise."
        ),
    },
}


def _build_chat_context(entries, history, chat_mode="open",
                        empathy_level=0.5, psyche_profile=None,
                        goals=None, recent_analysis_summary=None):
    """Build a rich context block for the chat system prompt."""
    context_parts = []

    # System prompt based on mode
    mode_info = CHAT_MODE_PROMPTS.get(chat_mode, CHAT_MODE_PROMPTS["open"])
    context_parts.append(mode_info["system"])

    # Empathy calibration
    if empathy_level <= 0.25:
        context_parts.append(
            "TONE: Be direct. Challenge their thinking without softening the edges. "
            "Respectful honesty, no cushioning."
        )
    elif empathy_level <= 0.5:
        context_parts.append(
            "TONE: Balance warmth with clarity. Validate what is real, "
            "then guide toward sharper perspective."
        )
    elif empathy_level <= 0.75:
        context_parts.append(
            "TONE: Lead with understanding. Prioritize making them feel seen, "
            "while weaving in observation where it serves."
        )
    else:
        context_parts.append(
            "TONE: Maximum gentleness. They may be in a fragile state. "
            "Keep responses brief, steady, and grounding. "
            "Warmth and presence above all else."
        )

    # Psyche profile
    if psyche_profile:
        values = psyche_profile.get("values", [])
        style = psyche_profile.get("support_style", "balanced")
        context_parts.append(
            f"USER PROFILE: Values: {', '.join(values) if values else 'not specified'}. "
            f"Preferred support style: {style}."
        )

    # Journal context
    if entries:
        recent = entries[:10]
        entry_summaries = []
        for e in recent:
            date = e.get("entry_date", "")[:10]
            sent = e.get("sentiment")
            sent_str = f" [sentiment: {sent:+.2f}]" if sent is not None else ""
            content = e.get("content", "")[:200]
            entry_summaries.append(f"  [{date}]{sent_str} {content}")

        context_parts.append(
            "RECENT JOURNAL ENTRIES (for context — reference naturally, "
            "don't list them back):\n" + "\n".join(entry_summaries)
        )

        # Quick pattern summary
        recent_sents = [
            e.get("sentiment", 0) for e in recent
            if e.get("sentiment") is not None
        ]
        if recent_sents:
            avg = sum(recent_sents) / len(recent_sents)
            trend_word = "positive" if avg > 0.1 else ("struggling" if avg < -0.1 else "mixed")
            context_parts.append(
                f"MOOD CONTEXT: Recent average sentiment is {avg:+.2f} ({trend_word})."
            )

        # Distortions detected recently
        recent_dists = []
        for e in recent[:5]:
            dists = detect_cognitive_distortions(e.get("content", ""))
            if dists:
                for d in dists:
                    recent_dists.append(d["label"])
        if recent_dists:
            context_parts.append(
                f"THINKING PATTERNS NOTICED: {', '.join(set(recent_dists))}. "
                "If these come up naturally, gently point them out."
            )

    # Active goals context
    if goals:
        active_goals = [g for g in goals if g.get("status") == "active"]
        if active_goals:
            goals_lines = []
            for g in active_goals[:5]:
                title = g.get("title", "")
                progress = g.get("progress", 0)
                goals_lines.append(f"  - {title} (progress: {progress:.0f}%)")
            context_parts.append(
                "ACTIVE GOALS:\n" + "\n".join(goals_lines)
            )

    # Recent analysis insights
    if recent_analysis_summary:
        context_parts.append(
            f"RECENT INSIGHTS: {recent_analysis_summary}"
        )

    # Response length guidance
    context_parts.append(
        "RESPONSE GUIDELINES:\n"
        "- When they're having a hard time: Keep it short (2-4 sentences), "
        "steady, and let them know you hear them.\n"
        "- When they're exploring: Offer richer reflections (1-2 paragraphs) with "
        "follow-up questions.\n"
        "- When they ask for advice: Give thoughtful, specific suggestions.\n"
        "- Always end with either a reflection or a gentle question - not both.\n"
        "- Never diagnose. Frame what you notice as patterns to explore.\n"
        "- If you pick up on crisis language, respond with grounded support and include "
        "crisis resources (988 Lifeline, Crisis Text Line)."
    )

    return "\n\n".join(context_parts)


def ai_chat(message, entries, history, api_key,
            model="gemini-2.5-flash", chat_mode="open",
            empathy_level=0.5, psyche_profile=None, goals=None,
            recent_analysis_summary=None):
    """Send a chat message to Gemini with full context."""

    # ── Crisis check ─────────────────────────────────────────────
    if detect_crisis(message):
        crisis_response = _call_gemini(
            f"""The person you are speaking with has expressed something that indicates 
real distress. Respond with grounded care and clarity:
1. Acknowledge what they have shared directly and honestly (2-3 sentences, genuine concern)
2. Offer one immediate grounding technique (the 5-4-3-2-1 senses exercise)
3. Present these resources clearly and without hesitation

Their message: "{message}"

Be steady and direct. Include these resources:
- 988 Suicide & Crisis Lifeline: Call or text 988 (24/7)
- Crisis Text Line: Text HOME to 741741
- International: https://www.iasp.info/resources/Crisis_Centres/

Close with something grounded: "Speaking about this matters. It takes real courage." """,
            api_key, model, temperature=0.3, max_tokens=1000,
        )
        return crisis_response

    # ── Build context ────────────────────────────────────────────
    system_context = _build_chat_context(
        entries, history, chat_mode, empathy_level, psyche_profile,
        goals=goals, recent_analysis_summary=recent_analysis_summary,
    )

    # Build conversation
    conv_parts = [system_context]

    # Include recent history (up to last 20 messages for context)
    recent_history = history[-20:] if len(history) > 20 else history
    for msg in recent_history:
        role_label = "User" if msg["role"] == "user" else "MindMirror"
        conv_parts.append(f"{role_label}: {msg['content']}")

    conv_parts.append(f"User: {message}")
    conv_parts.append("MindMirror:")

    prompt = "\n\n".join(conv_parts)

    return _call_gemini(prompt, api_key, model, temperature=0.7, max_tokens=2000)


# ══════════════════════════════════════════════════════════════════
#  AI REFLECTION PROMPTS
# ══════════════════════════════════════════════════════════════════

def ai_reflection_prompts(entries, api_key, model="gemini-2.5-flash",
                          goals=None, psyche_profile=None):
    """Generate personalised reflection prompts using AI."""
    recent = entries[:10]
    entry_block = "\n".join(
        f"[{e.get('entry_date', '')}] {e.get('content', '')[:200]}"
        for e in recent
    )

    goals_context = ""
    if goals:
        active_goals = [g for g in goals if g.get("status") == "active"]
        if active_goals:
            goals_context = "\nActive goals: " + ", ".join(
                g.get("title", "") for g in active_goals[:5]
            )

    profile_context = ""
    if psyche_profile:
        profile_context = f"\nUser values: {json.dumps(psyche_profile)}"

    prompt = f"""Based on these recent journal entries, generate 5 reflection questions 
that will create genuine insight. Questions that illuminate what this person 
cannot yet see on their own.

ENTRIES:
{entry_block}
{goals_context}
{profile_context}

GUIDELINES:
- Each question should target a specific pattern or theme from their entries
- Mix introspective questions with action-oriented ones
- Include one that highlights existing strength
- Include one that illuminates a cognitive blind spot
- Make each question specific to this person, never generic
- Add a brief (1-sentence) note on why you are asking
- Use emoji sparingly

Format each as:
**Prompt N:** [the question]
*Why this matters:* [brief note]"""

    return _call_gemini(prompt, api_key, model, temperature=0.8, max_tokens=1500)


# ══════════════════════════════════════════════════════════════════
#  SESSION SUMMARY & HOMEWORK
# ══════════════════════════════════════════════════════════════════

def generate_session_summary(chat_messages, api_key,
                             model="gemini-2.5-flash"):
    """Generate a summary of a chat session with key takeaways
    and gentle next steps."""
    if not chat_messages:
        return "No messages to summarise."

    convo = "\n".join(
        f"{'User' if m['role'] == 'user' else 'MindMirror'}: "
        f"{m['content'][:300]}"
        for m in chat_messages[-30:]
    )

    prompt = f"""Review this conversation and write a precise, meaningful recap.

CONVERSATION:
{convo}

WRITE:
1. **Core focus** - One sentence capturing the essential thread explored.

2. **Key moments** - 2-3 points where something shifted or crystallized.
   Be specific about what emerged.

3. **The movement** - How the emotional or intellectual ground shifted 
   from start to finish. (e.g., "Began with confusion about work, 
   uncovered a boundary issue, ended with clarity on next steps.")

4. **Strengths demonstrated** - 1-2 qualities they brought to this 
   conversation (honesty, willingness to sit with discomfort, etc.)

5. **Worth trying** - 2-3 small, specific actions they could take. 
   Frame as invitations. (e.g., "You might explore..." 
   "Worth experimenting with..." "A small test: ...")

VOICE: Direct, warm, concise. Speak to them ("You explored...").
Under 300 words."""

    return _call_gemini(prompt, api_key, model, temperature=0.5, max_tokens=1200)


# ══════════════════════════════════════════════════════════════════
#  NARRATIVE SUMMARY (Weekly / Monthly)
# ══════════════════════════════════════════════════════════════════

def generate_narrative_summary(entries, api_key,
                               model="gemini-2.5-flash",
                               local_data=None, period="week"):
    """Convert data into a compassionate narrative story with
    actionable recommendations and metaphors."""
    entry_block = "\n".join(
        f"[{e.get('entry_date', '')}] "
        f"(sent: {e.get('sentiment', 'N/A')}) "
        f"{e.get('content', '')[:200]}"
        for e in entries[:20]
    )

    data_summary = ""
    if local_data:
        data_summary += f"\nAverage sentiment: {local_data.get('avg_sentiment', 0):+.3f}"
        data_summary += f"\nMood trend: {local_data.get('mood_trend', {}).get('label', 'unknown')}"
        if local_data.get("topics"):
            data_summary += f"\nTop topics: {', '.join(list(local_data['topics'].keys())[:5])}"
        if local_data.get("emotions"):
            data_summary += f"\nDominant emotions: {', '.join(list(local_data['emotions'].keys())[:5])}"
        if local_data.get("growth_metrics"):
            gm = local_data["growth_metrics"]
            for metric in ["emotional_regulation", "resilience", "self_awareness"]:
                val = gm.get(metric)
                if val is not None:
                    data_summary += f"\n{metric.replace('_', ' ').title()}: {val}/100"

    prompt = f"""Write a "{period} in review" narrative for this person, 
drawn from their journal entries.

ENTRIES FROM THIS {period.upper()}:
{entry_block}

PATTERN DATA:
{data_summary}

WRITE:
A precise, evocative recap (250-400 words) that:
1. Narrates their {period} directly ("This {period}, you...")
2. Uses 1-2 resonant metaphors that illuminate rather than decorate
3. Honors the difficult alongside the strong with equal specificity
4. Names patterns and shifts with evidence
5. Offers 2-3 "what if" possibilities for the next stretch
   (e.g., "What if, next time [pattern] surfaces, you tried [alternative]?")
6. Closes with something honest and forward-looking

VOICE: Literary precision. Warm but never sentimental. 
The quality of prose that makes someone feel understood.
Use emoji sparingly (2-3 max)."""

    return _call_gemini(prompt, api_key, model, temperature=0.8, max_tokens=2000)


# ══════════════════════════════════════════════════════════════════
#  AI COGNITIVE DISTORTION ANALYSIS
# ══════════════════════════════════════════════════════════════════

def ai_distortion_analysis(entries, distortion_data, api_key,
                           model="gemini-2.5-flash"):
    """Use AI to provide deeper analysis of detected cognitive
    distortions with personalized reframes."""
    entry_block = "\n".join(
        f"[{e.get('entry_date', '')}] {e.get('content', '')[:300]}"
        for e in entries[:15]
    )

    dist_block = json.dumps(distortion_data, indent=2)

    prompt = f"""Analyze the cognitive patterns present in these journal entries with 
precision and compassion.

ENTRIES:
{entry_block}

DETECTED PATTERNS (from local analysis):
{dist_block}

PROVIDE:
1. **Dominant patterns** - Which distortions appear most frequently? How do they 
   interconnect (e.g., catastrophizing feeding into "should" statements)?

2. **Trigger contexts** - What situations, topics, or states activate these patterns?

3. **Precise reframes** - For each major pattern, offer a specific, grounded 
   alternative using their own language and circumstances.
   Format: "Instead of: [their thought] -> Consider: [reframe]"

4. **Practices** - 2-3 specific cognitive exercises they can apply.
   Name each clearly (e.g., "Evidence audit", "Thought record").

5. **Existing clarity** - Note entries where balanced thinking or self-correction 
   already appeared. Reinforce those moments.

IMPORTANT: 
- These patterns are universal, not defects
- Frame as habits to observe, not problems to solve
- This is pattern recognition, not diagnosis
- Write with precision and care"""

    return _call_gemini(prompt, api_key, model, temperature=0.6, max_tokens=2500)


# ══════════════════════════════════════════════════════════════════
#  MOOD FORECASTING (AI-enhanced)
# ══════════════════════════════════════════════════════════════════

def ai_mood_forecast(entries, local_data, api_key,
                     model="gemini-2.5-flash"):
    """Generate a compassionate mood forecast based on patterns."""
    entry_block = "\n".join(
        f"[{e.get('entry_date', '')}] (sent: {e.get('sentiment', 'N/A')}) "
        f"{e.get('content', '')[:150]}"
        for e in entries[:15]
    )

    pattern_data = ""
    if local_data:
        if local_data.get("mood_trend"):
            pattern_data += f"\nMood trend: {local_data['mood_trend']['label']} (slope: {local_data['mood_trend']['slope']:+.3f})"
        if local_data.get("day_of_week_patterns"):
            dow = local_data["day_of_week_patterns"]
            pattern_data += f"\nDay patterns: {json.dumps(dow)}"
        if local_data.get("triggers"):
            pattern_data += f"\nKnown triggers: {local_data['triggers'][:5]}"
        if local_data.get("topic_sentiment"):
            pattern_data += f"\nTopic-mood links: {json.dumps(dict(list(local_data['topic_sentiment'].items())[:5]))}"

    prompt = f"""Based on the patterns in their journal, create a precise 
"emotional weather forecast" for the coming days.

RECENT ENTRIES:
{entry_block}

PATTERN DATA:
{pattern_data}

CREATE A FORECAST THAT INCLUDES:

1. **🌤️ Outlook** - A concise, honest read on what is likely ahead 
   (use a weather metaphor only if it fits naturally)

2. **📅 Day-by-Day** - If day-of-week patterns exist, note which days 
   tend to be more demanding and which offer relief

3. **⚡ Watch for** - 1-2 specific triggers or patterns worth noticing early

4. **🛡️ What has worked** - 2-3 strategies that have historically 
   improved their state

5. **🌱 Opportunity** - One thing the coming days are well-suited for

VOICE: Confident and grounded. Concise (150-250 words). This is pattern-based 
observation, not prediction. Frame it as intelligence they can use, 
not fortune-telling."""

    return _call_gemini(prompt, api_key, model, temperature=0.8, max_tokens=1200)


# ══════════════════════════════════════════════════════════════════
#  MICRO-CELEBRATION GENERATOR
# ══════════════════════════════════════════════════════════════════

def generate_micro_celebration(entries, goals=None):
    """Generate warm micro-celebrations based on user activity.
    Returns list of celebration strings (local, no AI needed)."""
    celebrations = []

    if not entries:
        return celebrations

    # Streak celebration
    dates = sorted(set(
        e.get("entry_date", "")[:10] for e in entries
        if e.get("entry_date")
    ))
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        try:
            d1 = datetime.strptime(dates[i], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
            if (d1 - d2).days == 1:
                streak += 1
            else:
                break
        except ValueError:
            break

    if streak >= 7:
        celebrations.append(
            f"🔥 {streak} consecutive days. Consistency at this level is rare."
        )
    elif streak >= 3:
        celebrations.append(
            f"✨ {streak} days running. A rhythm is forming."
        )

    # Entry milestone
    count = len(entries)
    milestones = [5, 10, 25, 50, 100, 200, 500]
    for m in milestones:
        if count == m:
            celebrations.append(
                f"🎉 {m} entries. {m} acts of deliberate attention."
            )

    # Positive shift
    if len(entries) >= 5:
        recent_sents = [
            e.get("sentiment", 0) for e in entries[:3]
            if e.get("sentiment") is not None
        ]
        older_sents = [
            e.get("sentiment", 0) for e in entries[3:6]
            if e.get("sentiment") is not None
        ]
        if recent_sents and older_sents:
            recent_avg = sum(recent_sents) / len(recent_sents)
            older_avg = sum(older_sents) / len(older_sents)
            if recent_avg > older_avg + 0.2:
                celebrations.append(
                    "📈 Your recent entries show a measurable upward shift. "
                    "Something you are doing is working."
                )

    # Emotion diversity
    if len(entries) >= 3:
        all_emos = set()
        for e in entries[:5]:
            emos = detect_emotions(e.get("content", ""))
            if emos:
                all_emos.update(emos.keys())
        if len(all_emos) >= 5:
            celebrations.append(
                f"🎨 {len(all_emos)} distinct emotions named recently. "
                f"That emotional range is a genuine asset."
            )

    # Coping wins (detected positive entries after negative ones)
    if len(entries) >= 4:
        for i in range(len(entries) - 2):
            curr_sent = entries[i].get("sentiment", 0)
            prev_sent = entries[i + 1].get("sentiment", 0)
            if prev_sent is not None and curr_sent is not None:
                if prev_sent < -0.3 and curr_sent > 0.1:
                    celebrations.append(
                        "💪 You moved through a difficult stretch and came out the other side. "
                        "That is resilience in action."
                    )
                    break

    # Goal progress
    if goals:
        completed = [g for g in goals if g.get("status") == "completed"]
        if completed:
            celebrations.append(
                f"🏆 {len(completed)} goal"
                f"{'s' if len(completed) > 1 else ''} completed. "
                f"Intention followed by execution."
            )

    return celebrations[:3]  # max 3 at a time


# ══════════════════════════════════════════════════════════════════
#  COMMUNITY-LITE ANONYMIZED STATS
# ══════════════════════════════════════════════════════════════════

def get_community_stats():
    """Return anonymized 'you're not alone' style stats.
    These are approximate population-level norms, not from actual
    user data (since we don't aggregate across users)."""
    return {
        "midweek_stress": "42% of people report elevated stress on Wednesdays - a consistent midweek pattern",
        "sunday_anxiety": "35% experience anticipatory anxiety on Sunday evenings before the week begins",
        "mood_dips": "2-3 mood dips per week is the human baseline - not a sign of failure",
        "journaling_benefit": "Consistent journaling correlates with a 25% reduction in measurable stress markers",
        "sleep_mood": "Poor sleep correlates with 40% lower mood the following day - the connection is direct",
        "exercise_mood": "10 minutes of movement elevates mood for up to 2 hours - the threshold is lower than expected",
        "social_connection": "Brief social interaction improves mood state in 68% of people studied",
        "gratitude": "Noting 3 specific things you appreciate can shift baseline mood within 2 weeks",
    }


def get_relevant_community_stat(entries):
    """Pick a relevant community stat based on recent entry patterns."""
    stats = get_community_stats()
    if not entries:
        return stats["journaling_benefit"]

    recent = entries[:5]
    all_text = " ".join(e.get("content", "") for e in recent).lower()
    recent_sents = [
        e.get("sentiment", 0) for e in recent
        if e.get("sentiment") is not None
    ]
    avg = sum(recent_sents) / len(recent_sents) if recent_sents else 0

    if "sleep" in all_text or "tired" in all_text or "insomnia" in all_text:
        return stats["sleep_mood"]
    elif "stress" in all_text or "overwhelm" in all_text:
        return stats["midweek_stress"]
    elif "sunday" in all_text or "monday" in all_text:
        return stats["sunday_anxiety"]
    elif "lonely" in all_text or "alone" in all_text:
        return stats["social_connection"]
    elif avg < -0.2:
        return stats["mood_dips"]
    elif "exercise" in all_text or "gym" in all_text or "walk" in all_text:
        return stats["exercise_mood"]
    else:
        return stats["gratitude"]


# ══════════════════════════════════════════════════════════════════
#  SKILL MODULES CONTENT
# ══════════════════════════════════════════════════════════════════

SKILL_MODULES = {
    "mindfulness": {
        "title": "🧘 Mindfulness Basics",
        "category": "mindfulness",
        "skills": [
            {
                "id": "mind_01",
                "name": "5-4-3-2-1 Grounding",
                "duration": "3 min",
                "description": (
                    "A sensory inventory that pulls attention out of thought "
                    "and into the present moment. Five senses, descending count, "
                    "immediate effect."
                ),
                "exercise": (
                    "Begin now. Move through each sense deliberately:\n"
                    "- **5 things you see** (notice texture, light, edges)\n"
                    "- **4 things you can touch** (feel temperature, weight, fabric)\n"
                    "- **3 things you hear** (layer the sounds: near, mid, far)\n"
                    "- **2 things you smell** (even subtle: air, paper, skin)\n"
                    "- **1 thing you taste** (whatever is present)\n\n"
                    "Notice the shift. You moved from abstraction to presence."
                ),
            },
            {
                "id": "mind_02",
                "name": "Box Breathing",
                "duration": "4 min",
                "description": (
                    "A 4-4-4-4 breathing protocol that directly activates "
                    "your parasympathetic nervous system. Used by high-performance "
                    "professionals under acute stress."
                ),
                "exercise": (
                    "Set a timer for 4 minutes. Follow this cadence:\n"
                    "- **Inhale** slowly: 1... 2... 3... 4...\n"
                    "- **Hold**: 1... 2... 3... 4...\n"
                    "- **Exhale** slowly: 1... 2... 3... 4...\n"
                    "- **Hold**: 1... 2... 3... 4...\n\n"
                    "Repeat. By the third cycle, your heart rate will respond."
                ),
            },
            {
                "id": "mind_03",
                "name": "Body Scan",
                "duration": "5 min",
                "description": (
                    "A systematic sweep of attention from feet to crown, "
                    "observing sensation without interpretation. Builds "
                    "interoceptive awareness."
                ),
                "exercise": (
                    "Close your eyes. Move attention through each region:\n"
                    "- **Feet**: Temperature, pressure, contact with ground\n"
                    "- **Legs**: Where is tension held? Where is it absent?\n"
                    "- **Stomach**: Tight, open, fluttering, still?\n"
                    "- **Chest**: Heartbeat, breath rhythm, expansion\n"
                    "- **Shoulders**: Let gravity take what you are holding\n"
                    "- **Face**: Soften jaw, brow, the space around your eyes\n"
                    "- **Crown**: Hold the whole body in awareness at once\n\n"
                    "Where you find tension, direct one slow breath there."
                ),
            },
        ],
    },
    "distress_tolerance": {
        "title": "🛟 Distress Tolerance",
        "category": "distress_tolerance",
        "skills": [
            {
                "id": "dist_01",
                "name": "TIPP Technique",
                "duration": "5 min",
                "description": (
                    "Temperature, Intense exercise, Paced breathing, "
                    "Progressive relaxation. A DBT protocol for acute "
                    "emotional overwhelm. Works with physiology, not against it."
                ),
                "exercise": (
                    "When emotional intensity peaks, apply in sequence:\n\n"
                    "**T - Temperature**: Splash cold water on your face "
                    "or hold ice. The mammalian dive reflex slows heart rate "
                    "within seconds.\n\n"
                    "**I - Intense Exercise**: 30 seconds of jumping jacks, "
                    "push-ups, or running in place. Channel the physiological "
                    "activation.\n\n"
                    "**P - Paced Breathing**: Extend the exhale beyond the inhale "
                    "(e.g., in for 4, out for 6). This signals safety to your "
                    "nervous system.\n\n"
                    "**P - Progressive Relaxation**: Tense each muscle group "
                    "for 5 seconds, then release completely."
                ),
            },
            {
                "id": "dist_02",
                "name": "STOP Skill",
                "duration": "2 min",
                "description": (
                    "Stop, Take a step back, Observe, Proceed mindfully. "
                    "A circuit-breaker between stimulus and reaction."
                ),
                "exercise": (
                    "When you feel the pull toward reaction:\n\n"
                    "**S - Stop**: Freeze. Do not act on the impulse.\n\n"
                    "**T - Take a step back**: Create physical or mental distance. "
                    "One breath.\n\n"
                    "**O - Observe**: What is happening internally? "
                    "What triggered this? What are the facts versus the narrative?\n\n"
                    "**P - Proceed mindfully**: Choose your response from "
                    "your values, not your reactivity."
                ),
            },
            {
                "id": "dist_03",
                "name": "Radical Acceptance",
                "duration": "5 min",
                "description": (
                    "Acknowledging reality without judgment or resistance. "
                    "Acceptance is not approval. It is the decision to stop "
                    "adding suffering to pain."
                ),
                "exercise": (
                    "Identify something you are struggling to accept.\n\n"
                    "Repeat with intention:\n"
                    "- \"This is what is happening right now.\"\n"
                    "- \"I cannot change what has already occurred.\"\n"
                    "- \"Resisting reality adds suffering to pain.\"\n"
                    "- \"I can accept this AND work toward change.\"\n\n"
                    "Notice: acceptance often arrives as a physical release - "
                    "a softening in the chest, a dropped breath. That is "
                    "the body letting go of the fight."
                ),
            },
        ],
    },
    "self_compassion": {
        "title": "💗 Self-Compassion",
        "category": "self_compassion",
        "skills": [
            {
                "id": "comp_01",
                "name": "Self-Compassion Break",
                "duration": "3 min",
                "description": (
                    "Kristin Neff's three-component practice: mindfulness, "
                    "common humanity, and self-kindness. A complete "
                    "reorientation in under three minutes."
                ),
                "exercise": (
                    "When self-criticism arrives:\n\n"
                    "**1. Mindfulness**: \"This is a moment of suffering.\" "
                    "(Name it precisely. Do not minimize or amplify.)\n\n"
                    "**2. Common Humanity**: \"This is part of being human. "
                    "I am not alone in this experience.\" "
                    "(Connect to the universality of struggle.)\n\n"
                    "**3. Self-Kindness**: Place a hand on your chest and say: "
                    "\"May I offer myself the same compassion I would give "
                    "someone I love.\"\n\n"
                    "Stay with the intention. Let it settle."
                ),
            },
            {
                "id": "comp_02",
                "name": "Letter to Yourself",
                "duration": "10 min",
                "description": (
                    "Write from the perspective of someone who sees your "
                    "situation with complete clarity and unconditional regard."
                ),
                "exercise": (
                    "Imagine someone who understands your full context - "
                    "your pain and your strength in equal measure.\n\n"
                    "Write a letter from their perspective:\n"
                    "- What would they say about what you are facing?\n"
                    "- How would they name what you are feeling?\n"
                    "- What would they want you to remember?\n"
                    "- What strength would they point to as evidence?\n\n"
                    "Read it back slowly. These words are as true as "
                    "anything your inner critic has said."
                ),
            },
            {
                "id": "comp_03",
                "name": "Rewriting the Inner Critic",
                "duration": "5 min",
                "description": (
                    "Identify the critic's recurring script and rewrite it "
                    "with the precision of a skilled coach."
                ),
                "exercise": (
                    "**Step 1**: Write down one statement your inner "
                    "critic repeats. (e.g., \"You always fail at this.\")\n\n"
                    "**Step 2**: Ask: Would you say this to someone you "
                    "respect? What does it cost you to believe it?\n\n"
                    "**Step 3**: Rewrite it with accuracy and compassion:\n"
                    "\"This is difficult, and difficulty is not evidence of "
                    "inadequacy. What can I learn here?\"\n\n"
                    "**Step 4**: Each time the critic speaks, respond with "
                    "your rewrite. Repetition builds the new path."
                ),
            },
        ],
    },
    "cognitive_skills": {
        "title": "🧠 Cognitive Skills",
        "category": "cognitive_skills",
        "skills": [
            {
                "id": "cog_01",
                "name": "Thought Record",
                "duration": "10 min",
                "description": (
                    "The foundational CBT tool: capture a thought, weigh "
                    "evidence on both sides, and construct a more accurate "
                    "alternative."
                ),
                "exercise": (
                    "Use this structure:\n\n"
                    "**Situation**: What happened?\n"
                    "**Automatic Thought**: What went through your mind?\n"
                    "**Emotion** (0-100): What did you feel, and how intensely?\n"
                    "**Evidence FOR** the thought:\n"
                    "**Evidence AGAINST** the thought:\n"
                    "**Balanced Thought**: A more accurate perspective\n"
                    "**New Emotion** (0-100): What do you feel now?\n\n"
                    "Most people observe a 20-40 point reduction in emotional "
                    "intensity after completing this exercise."
                ),
            },
            {
                "id": "cog_02",
                "name": "Cognitive Defusion",
                "duration": "3 min",
                "description": (
                    "An ACT technique for creating distance between you and "
                    "your thoughts. Treats thoughts as mental events rather "
                    "than facts."
                ),
                "exercise": (
                    "When a painful thought grips you:\n\n"
                    "**Technique 1 - \"I notice\"**: Instead of \"I am a failure,\" "
                    "say \"I notice I am having the thought that I am a failure.\"\n\n"
                    "**Technique 2 - Displacement**: Repeat the thought in an "
                    "absurd voice. Observe how its authority dissolves.\n\n"
                    "**Technique 3 - Leaves on a stream**: Visualize each thought "
                    "as a leaf on moving water. Watch them arrive and pass.\n\n"
                    "The goal is not to eliminate thoughts. It is to hold them "
                    "without being held by them."
                ),
            },
            {
                "id": "cog_03",
                "name": "Values Compass",
                "duration": "10 min",
                "description": (
                    "Map your core values and measure current alignment. "
                    "Clarifies where energy should flow and where it is leaking."
                ),
                "exercise": (
                    "For each domain, rate importance (1-10) and "
                    "current alignment (1-10):\n\n"
                    "- **Relationships**: importance ___ / alignment ___\n"
                    "- **Work/Purpose**: importance ___ / alignment ___\n"
                    "- **Health/Body**: importance ___ / alignment ___\n"
                    "- **Growth/Learning**: importance ___ / alignment ___\n"
                    "- **Play/Rest**: importance ___ / alignment ___\n"
                    "- **Community**: importance ___ / alignment ___\n\n"
                    "Find the largest gap. Choose ONE concrete action "
                    "to close it this week. Small and specific wins."
                ),
            },
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
#  REFLECTION JOURNEY TEMPLATES
# ══════════════════════════════════════════════════════════════════

REFLECTION_JOURNEYS = {
    "heartbreak": {
        "title": "💔 Navigate Heartbreak",
        "description": "A 5-day guided sequence for processing loss and rebuilding solid ground.",
        "days": [
            {
                "day": 1,
                "title": "Name the Storm",
                "prompt": (
                    "Write without editing. What are you feeling right now? "
                    "Where does the pain live in your body? What shape does it take? "
                    "Let language carry what you have been holding."
                ),
                "insight": "Precision in naming pain reduces its hold on you.",
            },
            {
                "day": 2,
                "title": "The Full Inventory of Loss",
                "prompt": (
                    "Beyond the person: what else ended? The future you built "
                    "in your mind? A version of yourself? A sense of certainty? "
                    "Name every loss inside this loss."
                ),
                "insight": "Heartbreak is compound grief. Naming each layer is how you process them separately.",
            },
            {
                "day": 3,
                "title": "The Unsent Letter",
                "prompt": (
                    "Write a letter that will never be delivered. Say everything: "
                    "the rage, the gratitude, the confusion, the tenderness. "
                    "Complete honesty with no audience."
                ),
                "insight": "Expression without performance allows emotions to move rather than calcify.",
            },
            {
                "day": 4,
                "title": "What You Are Keeping",
                "prompt": (
                    "What did this teach you that you would not give back? "
                    "What capacities did you discover? What will you carry forward, "
                    "and what are you deliberately setting down?"
                ),
                "insight": "Growth and grief are not mutually exclusive. Both can be true.",
            },
            {
                "day": 5,
                "title": "Letter to Your Future Self",
                "prompt": (
                    "Write to the version of yourself who has moved through this. "
                    "What do you want them to remember? What do you hope they have "
                    "learned? What do you want for them?"
                ),
                "insight": "Imagining a healed future is not denial. It is an act of trust in your own capacity.",
            },
        ],
    },
    "motivation": {
        "title": "🔥 Rediscover Motivation",
        "description": "A 5-day sequence for reconnecting with your drive when it has gone quiet.",
        "days": [
            {
                "day": 1,
                "title": "The Drain Inventory",
                "prompt": (
                    "What is consuming your energy right now? List without censoring: "
                    "obligations, people, recurring thoughts, habits. "
                    "Be precise and unflinching."
                ),
                "insight": "You cannot redirect energy you have not first accounted for.",
            },
            {
                "day": 2,
                "title": "Spark Archaeology",
                "prompt": (
                    "When did you last feel genuinely energized and absorbed? "
                    "What were you doing? Who was present? What conditions "
                    "made it possible? Describe it with sensory detail."
                ),
                "insight": "Past states of flow contain precise data about what fuels you.",
            },
            {
                "day": 3,
                "title": "The Permission Slip",
                "prompt": (
                    "Write yourself explicit permission. To rest without earning it. "
                    "To want more. To change direction. To be mid-process. "
                    "What permission have you been withholding?"
                ),
                "insight": "Motivation often returns the moment you stop demanding it.",
            },
            {
                "day": 4,
                "title": "The Minimum Viable Step",
                "prompt": (
                    "If your most important goal felt impossible, what is the "
                    "smallest action that would take under two minutes? "
                    "Something almost absurdly easy. Name it. Then do it."
                ),
                "insight": "Momentum begins with motion, not inspiration.",
            },
            {
                "day": 5,
                "title": "The Energy Architecture",
                "prompt": (
                    "Design your ideal week. Not perfect, but sustainable. "
                    "Where does energy go? Where is rest protected? "
                    "What gets more of you, and what gets less?"
                ),
                "insight": "Motivation is not found. It is engineered through structure and intention.",
            },
        ],
    },
    "anxiety": {
        "title": "🌊 Understand Your Anxiety",
        "description": "A 5-day sequence for developing a working relationship with anxiety rather than warring against it.",
        "days": [
            {
                "day": 1,
                "title": "Map the Terrain",
                "prompt": (
                    "Describe your anxiety as precisely as you can. "
                    "What activates it? Where does it manifest in your body? "
                    "Does it have a pattern, a rhythm, a voice? What does it say?"
                ),
                "insight": "Observation creates distance. Distance creates choice.",
            },
            {
                "day": 2,
                "title": "The Complete Download",
                "prompt": (
                    "Set a timer for 10 minutes. Write every worry you are carrying. "
                    "Large, small, rational, absurd. All of them. "
                    "Then categorize: what can you influence versus what you cannot?"
                ),
                "insight": "Externalized worries lose their ability to loop. The page holds them so your mind does not have to.",
            },
            {
                "day": 3,
                "title": "The Signal Beneath",
                "prompt": (
                    "What is your anxiety attempting to protect you from? "
                    "If its intention were positive, however distorted the method, "
                    "what would it be trying to say? Acknowledge it, then negotiate."
                ),
                "insight": "Anxiety frequently carries valid information wrapped in disproportionate fear.",
            },
            {
                "day": 4,
                "title": "Your Evidence-Based Toolkit",
                "prompt": (
                    "List everything that has ever reduced your anxiety, "
                    "even marginally. People, environments, activities, "
                    "thoughts, rituals. Rate each 1-10 for reliability."
                ),
                "insight": "You already have more tools than you are currently using. This list makes them visible.",
            },
            {
                "day": 5,
                "title": "Coexistence",
                "prompt": (
                    "Imagine a life where anxiety is present but not governing. "
                    "What would you do? What would you say yes to? "
                    "What would be different? Write that life into detail."
                ),
                "insight": "The goal is not the absence of anxiety. It is a life worth living alongside it.",
            },
        ],
    },
    "self_worth": {
        "title": "💎 Rebuild Self-Worth",
        "description": "A 5-day sequence for reconnecting with your inherent value beneath the noise of self-doubt.",
        "days": [
            {
                "day": 1,
                "title": "The Evidence Record",
                "prompt": (
                    "List 10 things you have accomplished, survived, or contributed "
                    "at any point in your life. Include things others have valued in you. "
                    "They can be quiet victories. Write them as facts."
                ),
                "insight": "Low self-worth filters evidence. This exercise corrects the filter.",
            },
            {
                "day": 2,
                "title": "Source the Voice",
                "prompt": (
                    "When the 'not enough' narrative appears, whose voice is it? "
                    "A parent? A past relationship? A cultural expectation? "
                    "Trace the belief to its origin. Is it yours, or inherited?"
                ),
                "insight": "Many beliefs about worth were installed, not chosen. You can examine what you did not author.",
            },
            {
                "day": 3,
                "title": "Beyond Achievement",
                "prompt": (
                    "Describe your value without referencing any accomplishment, "
                    "title, or role. Who are you at the level beneath performance? "
                    "What qualities are constant regardless of output?"
                ),
                "insight": "Identity that depends on achievement is identity held hostage. You exist beneath what you do.",
            },
            {
                "day": 4,
                "title": "The External Mirror",
                "prompt": (
                    "Ask someone you trust: 'What do you value about me?' "
                    "Record their answer here. What resonates? "
                    "What is difficult to accept, and why?"
                ),
                "insight": "Others often perceive us with more accuracy than we perceive ourselves.",
            },
            {
                "day": 5,
                "title": "The New Terms",
                "prompt": (
                    "Write a new agreement with yourself. What will you choose "
                    "to believe about your worth? What will you stop tolerating? "
                    "What will you begin protecting?"
                ),
                "insight": "Self-worth is a daily practice, not a destination you arrive at once.",
            },
        ],
    },
}


# ══════════════════════════════════════════════════════════════════
#  GROUNDING EXERCISES (for proactive prompts)
# ══════════════════════════════════════════════════════════════════

GROUNDING_EXERCISES = [
    {
        "name": "5-4-3-2-1 Senses",
        "instruction": (
            "Anchor yourself in the present: Name **5 things you see**, "
            "**4 you can touch**, **3 you hear**, **2 you smell**, **1 you taste**. "
            "Notice your attention shift from thought to sensation."
        ),
    },
    {
        "name": "Box Breathing",
        "instruction": (
            "Inhale for 4 counts. Hold for 4. Exhale for 4. Hold for 4. "
            "Repeat 4 cycles. Your nervous system will follow the rhythm."
        ),
    },
    {
        "name": "Cold Water Reset",
        "instruction": (
            "Run cold water over your wrists for 30 seconds, or splash "
            "your face. The temperature change activates your dive reflex "
            "and interrupts the stress loop."
        ),
    },
    {
        "name": "Progressive Muscle Release",
        "instruction": (
            "Starting at your feet, tense each muscle group for 5 seconds, "
            "then release completely. Move upward to your face. "
            "Follow the contrast between tension and release."
        ),
    },
    {
        "name": "Gratitude Anchor",
        "instruction": (
            "Name 3 things you are genuinely grateful for in this moment. "
            "Be specific. The smaller and more concrete, the better."
        ),
    },
]

import random

def get_proactive_prompt(entries):
    """Choose a proactive prompt based on user patterns.
    Returns dict with type, message, and optional exercise."""
    if not entries:
        return {
            "type": "welcome",
            "message": "Welcome. Your first journal entry unlocks personalized insights. ✨",
            "exercise": None,
        }

    latest = entries[0]
    latest_sent = latest.get("sentiment", 0)
    latest_content = latest.get("content", "").lower()

    # Check for declining trend
    if len(entries) >= 3:
        recent_sents = [
            e.get("sentiment", 0) for e in entries[:3]
            if e.get("sentiment") is not None
        ]
        if recent_sents and all(s < -0.2 for s in recent_sents):
            exercise = random.choice(GROUNDING_EXERCISES)
            return {
                "type": "grounding",
                "message": (
                    "Your recent entries suggest a difficult stretch. "
                    "This may help right now:"
                ),
                "exercise": exercise,
            }

    # Check for specific themes
    if any(w in latest_content for w in ["sleep", "insomnia", "tired", "exhausted"]):
        return {
            "type": "checkin",
            "message": (
                "Sleep has been surfacing in your writing. How is your rest? "
                "A brief body scan before bed can quiet an active mind. 🌙"
            ),
            "exercise": None,
        }

    if latest_sent is not None and latest_sent > 0.3:
        return {
            "type": "amplify",
            "message": (
                "You are in a strong place right now. ✨ What is contributing? "
                "Naming what works makes it easier to return here."
            ),
            "exercise": None,
        }

    # Default: journaling cue
    cues = [
        "How are you actually doing today? Not the polished version.",
        "What is occupying the most mental space right now?",
        "Name one thing from this week that deserves acknowledgment, however small.",
        "What would you tell a younger version of yourself about what you are navigating?",
    ]
    return {
        "type": "journaling_cue",
        "message": random.choice(cues),
        "exercise": None,
    }


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 3 — analyzer.py is now complete.
# Next: CHUNK 4 (themes.py)
# ──────────────────────────────────────────────────────────────────
