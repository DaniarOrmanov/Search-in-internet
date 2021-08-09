# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для
# конкретного пользователя, сохранить JSON-вывод в файле *.json.

import requests
import json

url = 'https://api.github.com/users/DaniarOrmanov/repos'
response = requests.get(url)
j_data = response.json()

dict1 = {}
j = 0
for e in j_data:
    for key, value in e.items():
        if (key == 'name'):
            dict1.update({j: value})
            j += 1

d = open('file_json', 'w+')
json.dump(dict1, d)

print(dict1)              # Чтобы посмотреть на результат


