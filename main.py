import requests
from pathlib import Path
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_book(id):
    url = 'http://tululu.org/txt.php'
    payload = {'id': id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    print(response.history)
    try:
        check_for_redirect(response)
        file_path = Path(f'books/id{id}.txt')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wt') as file:
            file.write(response.text)
    except requests.HTTPError:
        print('Книга не найдена')


def parse_book_title_and_author(id):
    url = f'http://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    print(response.history)
    try:
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        h1_tag = soup.find('h1')
        h1_text = h1_tag.get_text()
        title, author = h1_text.split('::')
        title = title.strip()
        author = author.strip()
        print(title, author)
    except requests.HTTPError:
        pass


for i in range(10):
    parse_book_title_and_author(i+1)
