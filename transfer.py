import json

with open("static/JSON/sources.json", "r") as f:
    sources = json.load(f)[0]
for source in sources.keys():
    sources[source]["onclick"]=""
with open("static/JSON/sources.json", "w") as f:
    f.write(json.dumps(sources, indent=4))