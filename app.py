from flask import Flask, session, request, jsonify, render_template
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config.update(ENV='development')
app.config.update(SECRET_KEY='878as7d8f7997dfaewrwv8asdf8)(dS&A&*d78(*&ASD08A')

SESSION_KEY = "json"

def __default_message(message:str):
    # new_prompt = "Rephrase in NVC language " + message
    # new_prompt = "Rephrase the following in NVC Language. Be careful to distinguish pseudofeelings from feelings. \n" + message
    # new_prompt = "I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [Observations, Feelings, Needs,  Requests] after the rephrased text. here is the original text to rephrase: \""+ message + "\". I need the full response in json object including [original_txt, rephrased_txt, Observations, Feelings, Needs,  Requests]"
    # new_prompt = "I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [Observations, Feelings, Needs,  Requests] after the rephrased text. here is the original text to rephrase: \""+ message + "\". I need each of those [original_txt, rephrased_txt, Observations, Feelings, Needs,  Requests] in a seperate line without gab lines or prefix or postfix response explanation or start ."
    new_prompt = 'I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [observations, feelings, needs,  requests] after the rephrased text. here is the original text to rephrase: "'+ message + '". I need each of those keys [original_txt, rephrased_txt, observations, feelings, needs,  requests] in a seperate line - in the format of (key:value) and for each of the these keys [Observations, Feelings, Needs,  Requests] the value must be a valid array format even for single values ex(["val 1", "val 2"], ["val 1"], []) - without gab lines or prefix or postfix response explanation (example valid response: ' "original_txt:\"somevalue\"\nrephrased_txt: \"somevalue.\"\n\nobservations: somevaluesArray\nfeelings: somevaluesArray\nneeds: somevaluesArray\nrequests: somevaluesArray"')'

    ##########3###### old model
    # result = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=new_prompt,
    #     max_tokens=3000,
    #     temperature=1.2
    # )
    # return {"translation": result["choices"][0]["text"]}
    ################# new model
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": new_prompt},
        ],
        # max_tokens=3000,
        temperature=1.2
    )
    print(result)
    return {"translation": result["choices"][0]["message"]["content"]}


@app.route('/')
def home():
   return render_template("index.html")

@app.route("/translate", methods=["GET"])
def get():
    # get = session.get(SESSION_KEY)
    text = request.args.get("text")
    response = jsonify(__default_message(text), 200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response # For some reason the response comes back with leading \n's; trimming in js for now


@app.route("/post", methods=["POST"])
def post():
    post = request.get_json()
    print(post)
    
    if post is not None:
        session[SESSION_KEY] = post
        return jsonify(__default_message(post["text"]), 201)
    else:
        return jsonify(__default_message(message="wrong payload"), 400)

# app.run(host="127.0.0.1", port=5001, debug=True) # uncomment to run locally #runningLocally #ref
