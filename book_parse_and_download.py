import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, payload, folder):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        payload (dict): Параметры запроса.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    filename = sanitize_filename(filename) + '.txt'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wt') as file:
        file.write(response.text)
    return filepath


def download_image(url, folder):
    response = requests.get(url)
    response.raise_for_status()
    filename = unquote(urlsplit(url).path).split('/')[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    h1_tag = soup.select_one('h1')
    h1_text = h1_tag.get_text()
    title, author = h1_text.split('::')
    title = title.strip()
    author = author.strip()
    cover_link = urljoin(url, soup.select_one('.bookimage img')['src'])
    genre_tags = soup.select_one('span.d_book a')
    genres = [tag.text for tag in genre_tags]
    comment_tags = soup.select('div.texts span')
    comments = [tag.text for tag in comment_tags]
    parsed_book_page = {
        'title': title,
        'author': author,
        'cover_link': cover_link,
        'comments': comments,
        'genres': genres
    }
    return parsed_book_page