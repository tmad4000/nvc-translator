from flask import Flask, session, request, jsonify, render_template
import openai
import os
import time
import threading
import traceback
from collections import defaultdict, deque

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config.update(ENV='development')
app.config.update(SECRET_KEY='878as7d8f7997dfaewrwv8asdf8)(dS&A&*d78(*&ASD08A')

SESSION_KEY = "json"

# Modern chat model. text-davinci-003 (the original model) was deprecated and
# shut down by OpenAI in Jan 2024, which is why /translate started 500-ing.
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ---- Usage limits (all tunable via Heroku config vars, no redeploy needed) ----
RATE_PER_MIN = int(os.getenv("RATE_PER_MIN", "8"))         # per-IP, per minute
RATE_PER_DAY = int(os.getenv("RATE_PER_DAY", "150"))       # per-IP, per rolling 24h
GLOBAL_DAILY_CAP = int(os.getenv("GLOBAL_DAILY_CAP", "1500"))  # all users, per UTC day
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1000"))    # cap cost per request

# In-memory counters. Fine for a single gunicorn worker; resets on dyno restart
# (acceptable for abuse control). Move to Redis if the app is ever scaled out.
_lock = threading.Lock()
_ip_hits = defaultdict(deque)          # ip -> deque[timestamps] within last 24h
_global = {"day": None, "count": 0}    # global daily counter (UTC)

SYSTEM_PROMPT = (
    "You are an expert in Marshall Rosenberg's Nonviolent Communication (NVC). "
    "Rephrase the user's text in NVC language ('the language of life'). "
    "Carefully distinguish real feelings from pseudo-feelings: e.g. instead of "
    "'I feel abandoned' (a story/judgment), say 'I feel sad and lonely because my "
    "need for connection isn't met'. Also distinguish observations from judgments, "
    "needs from strategies, and requests from demands. "
    "Respond with ONLY the rephrased NVC version in warm, natural first-person "
    "language — no preamble, no labels, no quotation marks."
)


def _client_ip():
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _rate_limit_message():
    """Return a user-facing message if a limit is hit, else None (and record the hit)."""
    now = time.time()
    ip = _client_ip()
    with _lock:
        # Global daily cap (UTC day)
        day = time.strftime("%Y-%m-%d", time.gmtime(now))
        if _global["day"] != day:
            _global["day"] = day
            _global["count"] = 0
        if _global["count"] >= GLOBAL_DAILY_CAP:
            return ("The translator has reached its daily capacity. "
                    "Please try again tomorrow. 🦒")

        # Per-IP: prune entries older than 24h
        dq = _ip_hits[ip]
        while dq and now - dq[0] > 86400:
            dq.popleft()
        if not dq and ip in _ip_hits and len(_ip_hits) > 5000:
            # opportunistic memory cleanup of idle IPs
            _ip_hits.pop(ip, None)
            dq = _ip_hits[ip]

        if sum(1 for t in dq if now - t < 60) >= RATE_PER_MIN:
            return "You're translating quite fast — please wait a minute and try again."
        if len(dq) >= RATE_PER_DAY:
            return "You've reached today's translation limit. Please try again tomorrow."

        # Record the hit
        dq.append(now)
        _global["count"] += 1
        return None


def _translate(message: str):
    if not message or not message.strip():
        return {"translation": "Please enter some text to translate."}
    if len(message) > MAX_INPUT_CHARS:
        return {"translation": "That text is a bit long for the translator "
                               "(limit %d characters). Please shorten it and try again."
                               % MAX_INPUT_CHARS}
    limit_msg = _rate_limit_message()
    if limit_msg:
        return {"translation": limit_msg}
    try:
        result = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return {"translation": result["choices"][0]["message"]["content"].strip()}
    except Exception:
        traceback.print_exc()
        return {"translation": "Sorry — the translator hit an error and couldn't "
                               "complete this request. Please try again in a moment."}


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/translate", methods=["GET"])
def get():
    text = request.args.get("text")
    response = jsonify(_translate(text), 200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response  # response shape preserved: json[0].translation (see static/app.js)


@app.route("/post", methods=["POST"])
def post():
    post = request.get_json()

    if post is not None:
        session[SESSION_KEY] = post
        return jsonify(_translate(post.get("text", "")), 201)
    else:
        return jsonify(_translate(""), 400)

# app.run(host="127.0.0.1", port=5001, debug=True) # uncomment to run locally #runningLocally #ref
