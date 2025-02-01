import json
from flask import Flask, render_template, request
import sqlite3
import random
from collections import Counter

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'G@1v55k1b1d1cv5M@x1mv5'


@app.route('/')
def index():  # put application's code here
    db = sqlite3.connect('sources.db')
    sources = []
    for source in db.execute('SELECT * FROM sources WHERE USABLE = 1'):
        sources.append(source)
    db.close()
    random.shuffle(sources)
    return render_template("index.html", sources=sources)

@app.route('/source/<id>')
def source(id):
    db = sqlite3.connect('sources.db')
    cursor = db.execute('SELECT * FROM SOURCES WHERE ID = ?', (id,))
    source = []
    for row in cursor:
        for col in row:
            source.append(col)
    db.close()
    return render_template("source.html", source=source)

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

@app.route('/search_process', methods=["POST"])
def search_process():
    data = request.form
    tags = []
    countries = []
    keywds = []
    id = 0
    start_yr = 0
    end_yr = 0
    added = False
    for key, value in data.items():
        print(f"{key}: {value}")
        if "tag_" in key:
            tags.append(key.split("_")[1])
            print(tags)
        elif "country_" in key:
            countries.append(key.split("_")[1])
            print(countries)
        elif "keywds_" in key:
            keywds = data[key].split()
            print(keywds)
        elif "id_" in key and value != "":
            id = int(data[key])
        elif "start_" in key and value != "":
            start_yr = int(data[key])
        elif "end_" in key and value != "":
            end_yr = int(data[key])

    db = sqlite3.connect('sources.db')
    cmd = "SELECT * FROM SOURCES WHERE "
    if id != 0:
        cmd += f"ID = {id} AND "
        added = True;
    if start_yr != 0 and end_yr != 0:
        cmd += f"(YEAR BETWEEN {start_yr} AND {end_yr}) AND "
        added = True
    elif start_yr != 0:
        cmd += f"(YEAR BETWEEN {start_yr} AND {2025}) AND "
        added = True
    elif end_yr != 0:
        added = True
        cmd += f"(YEAR BETWEEN {0} AND {end_yr}) AND "

    if tags != []:
        tags = Counter(tags)
    else:
        tags = Counter("None")

    if countries != []:
        countries = Counter(countries)
    else:
        countries = Counter("None")

    if keywds != []:
        add_on = ""
        for key in keywds:
            add_on += f"TITLE LIKE %{key}% OR"
        add_on.removesuffix(" OR")
        cmd += f"({add_on}) AND "
        added = True
    cmd.removesuffix(" AND ")
    print(cmd)
    if added:
        cursor = db.execute(cmd)
    else:
        cursor = db.execute("SELECT * FROM SOURCES")
    sources = []
    for src in cursor:
        if tags - Counter(src[6].split("/")) == Counter() and countries - Counter(src[5].split("/")) == Counter():
            sources.append(src)
    db.close()

    '''for key, value in data.items():
        print(key, value)'''
    print(sources)
    return render_template("results.html", sources = sources)

if __name__ == '__main__':
    app.run()
