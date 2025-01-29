import json

from flask import Flask, render_template, request
import sqlite3
import random

app = Flask(__name__)



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
    return "skibidi"

if __name__ == '__main__':
    app.run()
