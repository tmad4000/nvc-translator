from flask import Flask, session, request, jsonify, render_template
import openai
import os
import traceback

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config.update(ENV='development')
app.config.update(SECRET_KEY='878as7d8f7997dfaewrwv8asdf8)(dS&A&*d78(*&ASD08A')

SESSION_KEY = "json"

# Modern chat model. text-davinci-003 (the original model) was deprecated and
# shut down by OpenAI in Jan 2024, which is why /translate started 500-ing.
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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


def __default_message(message: str):
    if not message or not message.strip():
        return {"translation": "Please enter some text to translate."}
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
    response = jsonify(__default_message(text), 200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response  # response shape preserved: json[0].translation (see static/app.js)


@app.route("/post", methods=["POST"])
def post():
    post = request.get_json()

    if post is not None:
        session[SESSION_KEY] = post
        return jsonify(__default_message(post["text"]), 201)
    else:
        return jsonify(__default_message(message="wrong payload"), 400)

# app.run(host="127.0.0.1", port=5001, debug=True) # uncomment to run locally #runningLocally #ref
