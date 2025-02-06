import sqlite3
import json

db = sqlite3.connect('sources.db')
c = db.cursor()
srcs = c.execute('SELECT * FROM SOURCES')
sources = []
sources.append({})

for src in srcs:
    sources[0][src[11]] = {
        "Title": src[0],
        "Month": src[1],
        "Date": src[2],
        "Year": src[3],
        "Author": src[4],
        "Countries": src[5].split("/"),
        "Tags": src[6].split("/"),
        "Description": src[7],
        "Source": src[8],
        "Path": src[10],
        "Link": src[13],
        "Scaled": src[12],
        "Attribution": src[14]
    }

with open('static/JSON/sources.json', 'w') as outfile:
    outfile.write(json.dumps(sources, indent=4))