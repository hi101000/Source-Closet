import requests

for i in range(1, 102):
    cont = requests.get(f"https://www.1000dokumente.de/images/9/93/0138_gpo_{i}.jpg?download").content
    with open('./static/Images/Image_'+str(i)+'.jpg', 'wb') as f:
        f.write(cont)