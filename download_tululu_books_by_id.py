import argparse
import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from book_parse_and_download import download_txt, download_image, parse_book_page


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
