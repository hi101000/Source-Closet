from flask import Flask, render_template
import sqlite3

app = Flask(__name__)



@app.route('/')
def index():  # put application's code here
    db = sqlite3.connect('sources.db')
    sources = []
    for source in db.execute('SELECT * FROM sources'):
        sources.append(source)
    db.close()
    return render_template("index.html", sources=sources)

@app.route('/source/<id>')
def source(id):
    db = sqlite3.connect('sources.db')
    cursor = db.execute('SELECT * FROM SOURCES WHERE ID = ?', (id,))
    source = []
    for row in cursor:
        for col in row:
            source.append(col)
    return render_template("source.html", source=source)

@app.route('/sources_abbr')
def sources_abbr():
    return render_template('Sources.html')

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/search_process')
def search_process():
    return "skibidi"

if __name__ == '__main__':
    app.run()
