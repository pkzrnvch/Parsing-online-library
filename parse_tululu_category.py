import argparse
import os
import json
from contextlib import suppress
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath

from book_parse_and_download import download_txt, download_image, parse_book_page


def get_end_page_to_parse(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    end_page = soup.select('.npage')[-1].text
    print(end_page)
    return end_page


def parse_category_for_book_urls(start_page, end_page, category_url):
    book_urls = []
    for page_to_parse in range(start_page, end_page+1):
        with suppress(requests.HTTPError):
            url = f'{category_url}{page_to_parse}/'
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            book_cards = soup.select('.d_book')
            for card in book_cards:
                link = card.select_one('a')['href']
                book_url = urljoin('https://tululu.org', link)
                book_urls.append(book_url)
    return book_urls


def download_tululu_book(url, book_folder, img_folder, skip_txt, skip_img):
    download_txt_url = 'https://tululu.org/txt.php'
    book_id = url.rsplit('b')[1].rstrip('/')
    parsed_book_page = parse_book_page(url)
    if not skip_txt:
        payload = {'id': book_id}
        book_path = download_txt(
            download_txt_url,
            parsed_book_page['title'],
            payload,
            book_folder
        )
        parsed_book_page['book_path'] = book_path
    if not skip_img:
        img_src = download_image(parsed_book_page['cover_link'], img_folder)
        parsed_book_page['img_src'] = img_src
    del parsed_book_page['cover_link']
    return parsed_book_page


def main():
    category_url = 'https://tululu.org/l55/'
    parser = argparse.ArgumentParser(
        description="This script downloads books, book covers "
                    "and parses book descriptions."
    )
    parser.add_argument(
        "--start_page",
        type=int,
        help="first category page to get books from",
        default=1,
    )
    parser.add_argument(
        "--end_page",
        type=int,
        help="last category page to get books from",
        default=get_end_page_to_parse(category_url),
    )
    parser.add_argument(
        "--dest_folder",
        help="destination folder",
        default='.',
    )
    parser.add_argument(
        "--skip_imgs",
        help="skip downloading book covers",
        action="store_true",
    )
    parser.add_argument(
        "--skip_txt",
        help="skip downloading .txt files",
        action="store_true",
    )
    parser.add_argument(
        "--json_path",
        help="path to the json file with downloaded books description",
        default='./downloaded_books.json',
    )
    args = parser.parse_args()
    book_folder = sanitize_filepath(f'{args.dest_folder}/books')
    img_folder = sanitize_filepath(f'{args.dest_folder}/images')
    json_path = sanitize_filepath(args.json_path)
    if json_path != 'downloaded_books.json':
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
    os.makedirs(book_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)
    print(type(args.end_page))
    book_urls = parse_category_for_book_urls(
        args.start_page,
        args.end_page,
        category_url,
    )
    downloaded_books = []
    for url in book_urls:
        with suppress(requests.HTTPError):
            downloaded_books.append(download_tululu_book(
                url,
                book_folder,
                img_folder,
                args.skip_txt,
                args.skip_imgs
            ))
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(downloaded_books, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
