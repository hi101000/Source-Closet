from flask import Flask, render_template, request, send_file, redirect, url_for, session
import random
from difflib import SequenceMatcher as SM
import similarity as sim
import sqlite3
import smtplib
from email.mime.text import MIMEText
import os
import string
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "5ecret_key_@69420_5kibid1"
app.permanent_session_lifetime = timedelta(minutes=30)


def get_tags(id: int, cursor) -> list:
    cursor.execute("SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)", (id,))
    # Convert tuple of tuples to list of tags
    tags = [t[0] for t in cursor.fetchall()]  # Fixed: properly extract tags from tuples
    return tags

def get_countries(id: int, cursor) -> list:
    cursor.execute("SELECT NAME FROM COUNTRIES WHERE ID IN (SELECT COUN_ID FROM SRC_COUNS WHERE SRC_ID=?)", (id,))
    # Convert tuple of tuples to list of tags
    couns = [c[0] for c in cursor.fetchall()]  # Fixed: properly extract tags from tuples
    return couns

def get_ser(id: int, cursor) -> list:
    cursor.execute("SELECT TITLE FROM SERIES WHERE ID IN (SELECT SER_ID FROM SRC_SERIES WHERE SRC_ID=?)", (id,))
    # Convert tuple of tuples to list of tags
    sers = [s[0] for s in cursor.fetchall()]  # Fixed: properly extract tags from tuples
    return sers

def send_bulk_emails(subject, body, sender, recipients, password):
    # Connect to Gmail's SMTP server using SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)  # Log in to the server

        # Loop over each recipient and send them an individual email
        for recipient in recipients:
            msg = MIMEText(body)  # Create a MIMEText object with the email body
            msg['Subject'] = subject  # Set the email's subject
            msg['From'] = sender  # Set the sender
            msg['To'] = recipient  # Set the current recipient

            smtp_server.sendmail(sender, recipient, msg.as_string())  # Send the email
            print(f"Message sent to {recipient}!")

class User:
    id = None
    psswd = None
    email = None
    uname = None
    def __init__(self, id, psswd, email, uname, key=None):
        self.id = id
        self.psswd = psswd
        self.email = email
        self.uname = uname
        self.key = key
    @staticmethod
    def get(user_id):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        user_data = cursor.execute("SELECT ID, PSSWD, EMAIL, UNAME FROM USERS WHERE ID=?", (user_id,)).fetchone()
        conn.close()
        if user_data:
            return User(*user_data)
        return None
    def is_authenticated(self):
        if self.id is not None and self.psswd is not None and self.email is not None and self.uname is not None:
            return True
        return False
    def is_anonymous(self):
        return False
    def get_id(self):
        return f"{self.id}"
    def is_active(self):
        return True

@app.route('/')
def index():  # put application's code here
    sources = []
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    src = cursor.execute("SELECT ID,DESCRIPTION,YEAR,MONTH,DATE,AUTHOR,PATH,LINK,CITATION,WIDTH,TITLE FROM SOURCES")
    src = src.fetchall()
    src_dict = {}
    for i in range(len(src)):
        # Get tags for the current source
        cursor.execute("SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)", (src[i][0],))
        ts = cursor.fetchall()
        # Convert tuple of tuples to list of tags
        tags = [t[0] for t in ts]  # Fixed: properly extract tags from tuples
        
        src_dict[str(src[i][0])] = {
            "Description": src[i][1],
            "Year": src[i][2],
            "Month": src[i][3],
            "Date": src[i][4],
            "Author": src[i][5],
            "Path": src[i][6],
            "Tags": tags,
            "Link": src[i][7],
            "Source": src[i][8],
            "Width": src[i][9],
            "Title": src[i][10] if len(src[i]) > 10 else None
        }
    src = src_dict
    del src_dict
    ids = src.keys()
    ids = list(ids)
    random.shuffle(ids)
    for i in range(9):
        sources.append([src[ids[i]], ids[i]])
    conn.close()
    return render_template("index.html", sources=sources, login=["user" in session.keys()][0])

@app.route('/browse')
def browse():
    sources = []
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    src = cursor.execute("SELECT ID,DESCRIPTION,YEAR,MONTH,DATE,AUTHOR,PATH,LINK,CITATION,WIDTH,TITLE FROM SOURCES")
    src = src.fetchall()
    src_dict = {}
    for i in range(len(src)):
        # Get tags for the current source
        cursor.execute("SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)", (src[i][0],))
        ts = cursor.fetchall()
        # Convert tuple of tuples to list of tags
        tags = [t[0] for t in ts]  # Fixed: properly extract tags from tuples
        
        src_dict[str(src[i][0])] = {
            "Description": src[i][1],
            "Year": src[i][2],
            "Month": src[i][3],
            "Date": src[i][4],
            "Author": src[i][5],
            "Path": src[i][6],
            "Tags": tags,
            "Link": src[i][7],
            "Source": src[i][8],
            "Width": src[i][9],
            "Title": src[i][10] if len(src[i]) > 10 else None
        }
    src = src_dict
    del src_dict
    ids = src.keys()
    ids = list(ids)
    random.shuffle(ids)
    for i in range(len(ids)):
        sources.append([src[ids[i]], ids[i]])
    conn.close()
    return render_template("browse.html", sources=sources, login=["user" in session.keys()][0])

@app.route('/source/<id>')
def source(id):
    source = []
    prot = False
    if id == "1":
        prot = True

    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    src = cursor.execute("SELECT ID,DESCRIPTION,YEAR,MONTH,DATE,AUTHOR,PATH,LINK,CITATION,WIDTH,TITLE,TRANS,ATTR,LICENSE_LINK FROM SOURCES WHERE ID=?", (id,))
    src = src.fetchall()[0]
    src = list(src)
    countries = cursor.execute("SELECT NAME FROM COUNTRIES WHERE ID IN (SELECT COUN_ID FROM SRC_COUNS WHERE SRC_ID=?)", (id,))
    countries = countries.fetchall()
    countries = [c[0] for c in countries]
    src.append(countries)
    tags = get_tags(int(id), cursor)
    src.append(tags)
    tag_ids = [t[0] for t in cursor.execute("SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?", (id,)).fetchall()]
    print(tag_ids)
    further = {}
    for tag_id in tag_ids:
        furt = cursor.execute("SELECT NAME, URL FROM FURTHER WHERE ID IN (SELECT FURT_ID FROM TAGS_FURTHER WHERE TAG_ID=?)", (tag_id,)).fetchall()
        for f in furt:
            further[f[0]] = f[1]
    conn.close()
    return render_template("source.html", source=src, prot=False if id != "1" else True, further=further, login=["user" in session.keys()][0])

@app.route('/sources_abbr')
def sources_abbr():
    return render_template('Sources.html', login=["user" in session.keys()][0])

@app.route('/about')
def about():
    return render_template("about.html", login=["user" in session.keys()][0])

@app.route('/search')
def search():
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    tags = [t[0] for t in cursor.execute("SELECT TAG FROM TAGS").fetchall()]

    countries = [c[0] for c in cursor.execute("SELECT NAME FROM COUNTRIES").fetchall()]
    conn.close()
    return render_template("search.html", tags=tags, countries=countries, login=["user" in session.keys()][0])

@app.route('/search_process', methods=["POST"])
def search_process():
    data = request.form
    tags = []
    countries = []
    keywds = []
    id = 0
    start_yr = 0
    end_yr = 0
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()

    num_entered = -1

    for key, value in data.items():
        if "tag_" in key:
            num_entered += 1
            tags.append(key.split("_")[1])
        elif "country_" in key:
            num_entered += 1
            countries.append(key.split("_")[1])
        elif "keywds_" in key:
            num_entered += 1
            keywds = value.lower().replace("-", " ").replace("\'", " ").replace("(", " ").replace("\"", " ").replace(")", " ").replace("[", " ").replace("]", " ").split(" ")
        elif "id_" in key and value != '':
            num_entered += 1
            id = int(value)
        elif "start_" in key and value != '':
            num_entered += 1
            start_yr = int(value)
        elif "end_" in key and value != '':
            num_entered += 1
            end_yr = int(value)

    if start_yr > end_yr:
        return render_template("error.html", error=f"The year range which you entered does not work physically. The starting year {start_yr} comes after the end year {end_yr}, which doesn't work. Please try again.")
    
    srcs = [s for s in cursor.execute("SELECT * FROM SOURCES").fetchall()]

    score  = 0.0
    results = []

    
    for src in srcs:
        src_tags = get_tags(src[0], cursor)
        src_countries = get_countries(src[0], cursor)
        score = 0
        if int(src[0]) == int(id):
            results.append((1000+num_entered, src[0], (src[1], src[2], src[3], src[4], src[5], src[6], src[7], src[8], src[9], src[10], get_tags(src[0], cursor))))
            continue
        elif id != 0 and int(src[0]) != int(id):
            score -= 1000
            continue
        if len(countries) != 0:
            intersec = len(set(src_countries).intersection(countries))
            if intersec == 0:
                score -= 5
                continue
            score += len(set(src_countries).intersection(set(countries)))
        if len(tags) != 0:
            intersec = len(set(src_tags).intersection(tags))
            if intersec == 0:
                score -= 5
                continue
            elif intersec > 0:
                score += intersec * 10
            score += intersec
        if len(keywds) != 0:
            if src[5] is not None:
                text = (src[10] + " " + src[1] + " " + src[5]).lower().replace("-", " ").replace("\'", " ").replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ").replace("\"", " ").split(" ") if src[10] is not None else src[1].lower().replace("-", " ").split(' ')
            else:
                text = (src[10] + " " + src[1]).lower().replace("-", " ").replace("\'", " ").replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ").replace("\"", " ").split(" ") if src[10] is not None else src[1].lower().replace("-", " ").split(' ')
            dist = sim.jaccard_distance(set(text), set(keywds))*20-20
            score += dist
        
        if start_yr != 0 and end_yr != 0 and (start_yr <= int(src[2]) <= end_yr):
            score += 2
        elif end_yr != 0 and start_yr != 0 and not (start_yr <= int(src[2]) <= end_yr):
            continue
        elif end_yr == 0 and start_yr != 0 and int(src[2]) >= start_yr:
            score += 2
        elif start_yr == 0 and end_yr != 0 and int(src[2]) <= end_yr:
            score += 2
        elif start_yr == 0 and end_yr == 0:
            pass

        if score > num_entered/1.5:
            results.append((score, src[0], (src[1], src[2], src[3], src[4], src[5], src[6], src[7], src[8], src[9], src[10], get_tags(src[0], cursor))))

    results.sort(reverse=True, key=lambda x: x[0])
    #TODO: Fix the way sources are added to the list
    ranked_sources = {key: value for _, key, value in results}
    ranked_sources = [ranked_sources]
    conn.close()
    return render_template("results.html", sources=ranked_sources, query=keywds, login=["user" in session.keys()][0])

@app.route('/.well-known/discord')
def discord():
    return 'dh=b423c40a76035ddef43e4d16052440ac71a9be4d'

@app.route('/sourceno/<ip>/<city>/<region>/<country>/<timezone>/<loc>/<provider>/<number>')
def sourceno(ip, city, region, country, timezone, loc, provider, number):
    redirect(url_for('source', id=number), code=302)
 
@app.route('/sitemap.txt')
def sitemap():
    with open('assets/sitemap.txt', 'r') as f:
        sitemap_content = f.read()
    return sitemap_content, 200, {'Content-Type': 'text/plain'}

@app.route('/robots.txt')
def robots():
    with open('assets/robots.txt', 'r') as f:
        robots_content = f.read()
    return robots_content, 200, {'Content-Type': 'text/plain'}

@app.route('/signup')
def signup():
    if "user" not in session.keys():
        token = ""
        chars = string.digits+string.ascii_letters
        for i in range(30):
            token+=random.choice(chars)
        conn = sqlite3.connect("sources.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS (TOKEN) VALUES (?)", (token,))
        conn.commit()
        conn.close()
        return render_template("signup.html", token=token, login=["user" in session.keys()][0])
    else:
        print(session.keys())
        return render_template("error.html", error="You are already logged in with an account.")

@app.route('/login')
def login():
    return render_template("login.html", login=["user" in session.keys()][0])

@app.route('/login_process', methods=["POST"])
def login_process():
    data = request.form
    token = data.get("token_", "")
    if token == "":
        return render_template("error.html", error="You did not enter a token. Please try again.")
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    user_data = cursor.execute("SELECT TOKEN FROM USERS").fetchall()
    conn.close()
    user_data = [u[0] for u in user_data]
    if token not in user_data:
        return render_template("error.html", error="The token you entered is not valid. Please try again.")
    else:
        session["user"] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if "user" not in session.keys():
        return render_template("error.html", error="You are not logged in. Please log in to view your profile.")
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    user_token = session["user"]
    sources = conn.execute("SELECT SRC_ID FROM USERS_SRCS WHERE UID=(?)", (user_token,)).fetchall()
    sources = [s[0] for s in sources]
    #                              0      1           2     3     4     5       6
    sources = conn.execute("SELECT ID, DESCRIPTION, YEAR, MONTH, DATE, AUTHOR, TITLE FROM SOURCES WHERE ID IN ({})".format(','.join('?' * len(sources))), sources).fetchall()
    sources = [list(s) for s in sources]
    return render_template("profile.html", sources=sources, login=["user" in session.keys()][0])

@app.route('/save_source/<int:id>')
def save_source(id: int):
    if "user" not in session.keys():
        return render_template("error.html", error="You are not logged in. Please log in to save sources.")
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    user_token = session["user"]
    cursor.execute("INSERT INTO USERS_SRCS (UID, SRC_ID) VALUES (?, ?)", (user_token, id))
    conn.commit()
    conn.close()
    return redirect(url_for('source', id=id))

@app.route('/delete_source/<int:id>')
def delete_source(id: int):
    if "user" not in session.keys():
        return render_template("error.html", error="You are not logged in. Please log in to delete sources.")
    conn = sqlite3.connect("sources.db")
    cursor = conn.cursor()
    user_token = session["user"]
    cursor.execute("DELETE FROM USERS_SRCS WHERE UID=? AND SRC_ID=?", (user_token, id))
    conn.commit()
    conn.close()
    return redirect(url_for('profile'))

@app.route('/dl')
def dl():
    if "user" not in session.keys():
        return render_template("error.html", error="You are not logged in. Please log in to download sources.")
    if session["user"] != "@GauisSkibidicusMaximus101000":
        return render_template("error.html", error="You are not allowed to access this page.")
    return send_file("sources.db", as_attachment=True, download_name="sources.db")

if __name__ == '__main__':
    app.run()
