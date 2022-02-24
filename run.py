import json
import glob
import requests
from bs4 import BeautifulSoup
import pandas as pd

session = requests.session()


def login():
    print('login....')
    datas = {
        'username': 'user',
        'password': 'user12345'
    }
    req = session.post('http://127.0.0.1:5000/login', data=datas)
    soup = BeautifulSoup(req.text, 'html5lib')

    page_item = soup.find_all('li', 'page-item')
    total_page = len(page_item) - 2  # delete next & previous page item

    return total_page


def get_urls(page):
    print(f'getting urls page {page}....')
    params = {
        'page': page
    }

    # manfaatkan file html yang sudah di download agar tidak selalu melakukan requests ke web saat mencari tag
    # soup = Beautifulsoup(open('res.html'), 'html5lib')

    req = session.get('http://127.0.0.1:5000/?', params=params)
    soup = BeautifulSoup(req.text, 'html5lib')

    title = soup.find_all('h4', 'card-title')
    urls = []
    for i in title:
        url = i.find('a')['href']
        urls.append(url)

    return urls


def get_detail(url):
    print(f'getting details url {url}....')
    req = session.get('http://127.0.0.1:5000' + url)
    soup = BeautifulSoup(req.text, 'html5lib')

    title = soup.find('title').text.strip()
    price = soup.find('h4', 'card-price').text.strip()
    stock = soup.find('span', 'card-stock').text.strip().replace('stock: ', '')
    category = soup.find('span', 'card-category').text.strip().replace('category: ', '')
    description = soup.find('p', 'card-text').text.strip().replace('Description: ', '')

    dict_data = {
        'title': title,
        'price': price,
        'stock': stock,
        'category': category,
        'description': description
    }

    with open(f"result/json/{url.replace('/', '')}.json", "w+") as filejson:
        json.dump(dict_data, filejson)


def create_alldata():
    print('all data generated....')
    files = sorted(glob.glob('result/json/*.json'))

    datas = []
    for i in files:
        with open(i) as jsonfile:
            data = json.load(jsonfile)
            datas.append(data)

    df = pd.DataFrame(datas)
    df.to_csv('result/all data csv.csv', index=False)
    df.to_excel('result/all data excel.xlsx', index=False)

    # merge all json data in one file
    with open('result/all_result_detail.json', 'w') as outfile:
        json.dump(datas, outfile)


def run():
    # get total page from login function
    total_pages = login()

    # get all link from all page
    total_urls = []
    for i in range(total_pages):
        page = i+1
        url = get_urls(page)
        total_urls += url

    with open('result/all_urls.json', 'w') as jsonurl:
        json.dump(total_urls, jsonurl)

    # read link from json file & get all detail
    with open('result/all_urls.json') as json_file:
        all_url = json.load(json_file)
    for i in all_url:
        get_detail(i)

    # get all data
    create_alldata()


run()

