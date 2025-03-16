import json
from flask import Flask, render_template, request
import random
from difflib import SequenceMatcher as SM
import similarity as sim

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'G@1v55k1b1d1cv5M@x1mv5'


@app.route('/')
def index():  # put application's code here
    sources = []
    with open('static/JSON/sources.json', 'r') as f:
        src = json.load(f)[0]
    ids = src.keys()
    ids = list(ids)
    random.shuffle(ids)
    for i in range(9):
        sources.append([src[ids[i]], ids[i]])
    return render_template("index.html", sources=sources)

@app.route('/source/<id>')
def source(id):
    source = []
    with open('static/JSON/sources.json', 'r') as f:
        src = json.load(f)[0]
    for key in src[f"{id}"].keys():
        source.append(src[f"{id}"][key])
    if isinstance(source[12], list):
        prot = True
    else:
        prot = False

    return render_template("source.html", source=source, id=id, prot=prot)

@app.route('/sources_abbr')
def sources_abbr():
    return render_template('Sources.html')

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/search')
def search():
    with open("static/JSON/tags.json", "r") as f:
        tags = json.loads(f.read())[0]["Tags"]
    with open("static/JSON/countries.json", "r") as f:
        countries = json.loads(f.read())[0]["Countries"]
    return render_template("search.html", tags=tags, countries=countries)

@app.route('/sitemap.txt')
def sitemap():
    with open("static/assets/sitemap.txt", "r") as f:
        smap = f.read()
    return smap

@app.route('/search_process', methods=["POST"])
def search_process():
    data = request.form
    sources = []
    tags = []
    countries = []
    keywds = []
    id = 0
    start_yr = 0
    end_yr = 0

    common_words = {"the", "a", "an", "and", "or", "but", "if", "in", "on", "at", "by", "for", "with", "about",
                    "against", "between", "into", "through", "during", "before", "after", "above", "below", "to",
                    "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once",
                    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
                    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
                    "s", "t", "can", "will", "just", "don", "should", "now"}

    for key, value in data.items():
        if "tag_" in key:
            tags.append(key.split("_")[1])
        elif "country_" in key:
            countries.append(key.split("_")[1])
        elif "keywds_" in key:
            keywds = value.lower().split(" ")
        elif "id_" in key and value != '':
            id = int(value)
        elif "start_" in key and value != '':
            start_yr = int(value)
        elif "end_" in key and value != '':
            end_yr = int(value)

    if start_yr > end_yr:
        return render_template("error.html", error=f"The year range which you entered does not work physically. The starting year {start_yr} comes after the end year {end_yr}, so that doesn't work.")

    with open("static/JSON/sources.json", "r") as f:
        src = json.load(f)[0]

    results = []

    for key, value in src.items():
        match_score = 0

        if id != 0 and id != int(key):
            continue
        elif id != 0 and id == int(key):
            match_score += 500

        if keywds != []:
            text = (value["Title"] + " " + value["Description"]).lower().split(' ')
            dist = sim.jaccard_distance(set(text), set(keywds))*10-10
            match_score += dist

        if tags != []:
            match_score += len(set(tags).intersection(set(value["Tags"])))
            if len(set(tags).intersection(set(value["Tags"]))) == 0:
                continue

        if countries:
            match_score += len(set(countries).intersection(set(value["Countries"])))
            if len(set(countries).intersection(set(value["Countries"]))) == 0:
                continue

        if start_yr != 0 and end_yr != 0 and (start_yr <= int(value["Year"]) <= end_yr):
            match_score += 1
        elif end_yr != 0 and start_yr != 0 and not (start_yr <= int(value["Year"]) <= end_yr):
            continue

        if match_score > 0.01:
            results.append((match_score, key, value))

    results.sort(reverse=True, key=lambda x: x[0])

    ranked_sources = {key: value for _, key, value in results}

    return render_template("results.html", sources=[ranked_sources])

if __name__ == '__main__':
    app.run()
