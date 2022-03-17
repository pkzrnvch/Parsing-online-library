import argparse
import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, payload=None, folder='./books/'):
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


def download_image(url, folder='./images/'):
    response = requests.get(url)
    response.raise_for_status()
    filename = unquote(urlsplit(url).path).split('/')[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(book_id):
    url = f'https://tululu.org/b{book_id}/'
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
    genre_tags = soup.find('span', class_='d_book').find_all('a')
    genres = [tag.text for tag in genre_tags]
    comment_tags = soup.find_all('div', class_='texts')
    comments = [tag.find('span').text for tag in comment_tags]
    parsed_book_page = {
        'title': title,
        'author': author,
        'cover_link': cover_link,
        'comments': comments,
        'genres': genres
    }
    return parsed_book_page


def download_tululu_book(book_id):
    url = 'https://tululu.org/txt.php'
    try:
        parsed_book_page = parse_book_page(book_id)
        payload = {'id': book_id}
        book_path = download_txt(url, f'{book_id}.{parsed_book_page["title"]}', payload)
        print('Заголовок:', parsed_book_page['title'])
        print('Автор:', parsed_book_page['author'])
        print('Жанры:', parsed_book_page['genres'])
        print('Путь:', book_path, '\n')
        download_image(parsed_book_page['cover_link'])
    except requests.HTTPError:
        print('Книга не найдена', '\n')


def main():
    parser = argparse.ArgumentParser(
        description="This script downloads books, book covers and parses book descriptions."
    )
    parser.add_argument("--start_id", type=int, help="id of the first book to download", default=1)
    parser.add_argument("--end_id", type=int, help="id of the last book to download", default=10)
    args = parser.parse_args()
    os.makedirs('./books', exist_ok=True)
    os.makedirs('./images', exist_ok=True)
    for book_id in range(args.start_id, args.end_id+1):
        download_tululu_book(book_id)


if __name__ == '__main__':
    main()
