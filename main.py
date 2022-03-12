import requests
from pathlib import Path

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

for i in range(10):
    download_book(i+1)
