'''import requests

for i in range(19, 34):
    cont = requests.get(f"https://s3.amazonaws.com/NARAprodstorage/lz/dc-metro/rg-242/7788344_T175/T175/T175-258A/T175-258-00{i}.jpg").content
    with open('./static/Images/Image_'+str(i)+'.jpg', 'wb') as f:
        f.write(cont)'''

'''from collections import Counter

c1 = Counter(["hi", "hello"])
c2 = Counter(["hola", "hi", "bye", "hello"])

print(c1-c2 == Counter())'''

'''import libsql

table = "TAGS_FURTHER"
conn_local = libsql.connect('static/sources.db')
cur_local = conn_local.cursor()

for row in cur_local.execute(f"SELECT * FROM {table}").fetchall():
    tag_exists = cur_local.execute("SELECT 1 FROM TAGS WHERE ID = ?", (row[1],)).fetchone()
    furt_exists = cur_local.execute("SELECT 1 FROM FURTHER WHERE ID = ?", (row[2],)).fetchone()
    if not tag_exists or not furt_exists:
        print(f"Invalid foreign key reference in row: {row}")
        if not tag_exists:
            print(f"  - TAG_ID {row[1]} does not exist in USERS table.")
        if not furt_exists:
            print(f"  - FURT_ID {row[2]} does not exist in SOURCES table.")'''