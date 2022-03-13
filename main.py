import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = sanitize_filename(filename) + '.txt'
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(filepath, 'wt') as file:
        file.write(response.text)
    return filepath


def parse_book_title_and_author(id):
    url = f'http://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    h1_tag = soup.find('h1')
    h1_text = h1_tag.get_text()
    title, author = h1_text.split('::')
    title = title.strip()
    author = author.strip()
    return title, author


def download_tululu_book(id):
    url = f'http://tululu.org/txt.php?id={id}'
    try:
        title, author = parse_book_title_and_author(id)
        print(download_txt(url, title))
    except requests.HTTPError:
        print('Книга не найдена')


for i in range(10):
    download_tululu_book(i+1)
