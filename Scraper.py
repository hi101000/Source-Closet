'''import requests

for i in range(19, 34):
    cont = requests.get(f"https://s3.amazonaws.com/NARAprodstorage/lz/dc-metro/rg-242/7788344_T175/T175/T175-258A/T175-258-00{i}.jpg").content
    with open('./static/Images/Image_'+str(i)+'.jpg', 'wb') as f:
        f.write(cont)'''

from collections import Counter

c1 = Counter(["hi", "hello"])
c2 = Counter(["hola", "hi", "bye", "hello"])

print(c1-c2 == Counter())