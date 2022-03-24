import argparse
import os
import json
from urllib.parse import unquote, urljoin, urlsplit
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_catogry_for_book_urls(start_page, end_page):
    book_urls = []
    for page_to_parse in range(start_page, end_page+1):
        url = f'https://tululu.org/l55/{page_to_parse}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_cards = soup.select('.d_book')
        for card in book_cards:
            link = card.select_one('a')['href']
            book_url = urljoin('https://tululu.org', link)
            book_urls.append(book_url)
        page_to_parse += 1
    return book_urls


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


def download_tululu_book(url):
    download_txt_url = 'https://tululu.org/txt.php'
    book_id = url.rsplit('b')[1].rstrip('/')
    try:
        parsed_book_page = parse_book_page(url)
        payload = {'id': book_id}
        book_path = download_txt(download_txt_url, parsed_book_page['title'], payload)
        parsed_book_page['book_path'] = book_path
        print('Заголовок:', parsed_book_page['title'])
        print('Автор:', parsed_book_page['author'])
        print('Жанры:', parsed_book_page['genres'])
        print('Путь:', book_path, '\n')
        img_src = download_image(parsed_book_page['cover_link'])
        parsed_book_page['img_src'] = img_src
        del parsed_book_page['cover_link']
        return parsed_book_page
    except requests.HTTPError:
        print('Книга не найдена', '\n')


def main():
    parser = argparse.ArgumentParser(
        description="This script downloads books, book covers and parses book descriptions."
    )
    parser.add_argument("--start_page", type=int, help="first category page to get books from", default=1)
    parser.add_argument("--end_page", type=int, help="last category page to get books from", default=4)
    args = parser.parse_args()
    os.makedirs('./books', exist_ok=True)
    os.makedirs('./images', exist_ok=True)
    book_urls = parse_catogry_for_book_urls(args.start_page, args.end_page)
    downloaded_books = []
    for url in book_urls:
        downloaded_books.append(download_tululu_book(url))
    pprint(downloaded_books)
    with open('./downloaded_books.json', 'w', encoding='utf-8') as json_file:
        json.dump(downloaded_books, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()

