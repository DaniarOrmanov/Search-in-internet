from bs4 import BeautifulSoup as bs
import requests
from pymongo import MongoClient
from pprint import pprint

def salary(sal_text):
    if sal_text == 'ЗП не указана!':
        first_num = 'не указано'
        second_num = 'не указано'
    else:
        unit = sal_text[sal_text.rfind(' '):]
        if sal_text.find(' – ') != -1:
            first_num = sal_text.split(' – ')[0][0:sal_text.find('\u202f')] + sal_text[sal_text.find('\u202f')+1:sal_text.find(' ')] + unit
            second_num = sal_text.split(' – ')[1][0:sal_text.find('\u202f')] + sal_text[sal_text.find('\u202f')+1:sal_text.find(' ')] + unit
        elif sal_text.find('от') != -1:
            num = sal_text.split(' ')[1]
            first_num = num.split('\u202f')[0] + num.split('\u202f')[1] + unit
            second_num = 'не указано'
        elif sal_text.find('до') != -1:
            first_num = 'не указано'
            num = sal_text.split(' ')[1]
            second_num = num.split('\u202f')[0] + num.split('\u202f')[1] + unit
    a = [first_num, second_num]
    return a

url = 'https://spb.hh.ru'

client = MongoClient('127.0.0.1', 27017)
db = client['hh']

vac = db.vac

pages = [0, 1, 3]              #список анализируемых страниц. отсчет ведется от нуля
for page in pages:
    params = {'clusters': 'true',
              'area': '2',
              'ored_clusters': 'true',
              'enable_snippets': 'true',
              'salary': 'None',
              'st': 'searchVacancy',
              'text': 'Python',
              'from': 'suggest_post',
              'page': page}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
    response = requests.get(url+'/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    i = 1
    for vacancy in vacancy_list:
        vacancy_data = {}
        vacancy_link = vacancy.find('a', attrs={'class': 'bloko-link'}).get('href')
        vacancy_name = vacancy.find('a', attrs={'target': '_blank'}).text
        try:
            vacancy_sal = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
        except BaseException:
            vacancy_sal = 'ЗП не указана!'
        sal = salary(vacancy_sal)
        vacancy_data.update({'Наименование': vacancy_name,
                             'Минимальная ЗП': sal[0],
                             'Максимальная ЗП': sal[1],
                             'Ссылка на вакансию': vacancy_link,
                             'Сайт': url})
        vac.update_one(
            {'Ссылка на вакансию': vacancy_data['Ссылка на вакансию']},
            {'$set': vacancy_data},
            upsert=True)
        i += 1

i = 1   #Порядковый номер вакансии, внесенной в базу.
for doc in vac.find({}):
    print(f'Вакансия №{i}')
    pprint(doc)
    i += 1

    