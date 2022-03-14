import requests
from urllib.parse import urljoin, urlsplit, unquote
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


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    filename = unquote(urlsplit(url).path).split('/')[-1]
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(id):
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
    cover_link = urljoin(url, soup.find(class_='bookimage').find('img')['src'])
    comment_tags = soup.find_all('div', class_='texts')
    comments = []
    for comment_tag in comment_tags:
        comments.append(comment_tag.find('span').text)
    parsed_book_page = {
        'title': title,
        'author': author,
        'cover_link': cover_link,
        'comments': comments,
    }
    return parsed_book_page


def download_tululu_book(id):
    url = f'http://tululu.org/txt.php?id={id}'
    try:
        parsed_book_page = parse_book_page(id)
        print(parsed_book_page)
        print(download_txt(url, parsed_book_page['author']))
        download_image(parsed_book_page['cover_link'])
    except requests.HTTPError:
        print('Книга не найдена')


for i in range(10):
    download_tululu_book(i+1)