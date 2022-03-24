# Online library parser

This script downloads books, book covers and parses book description from [tululu.org](https://tululu.org) website.

### How to install

Python3 should already be installed. Use pip (or pip3, in case of conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Usage

To run the program use the command below from the project directory. Use `--start_id`(1 by default) and `--end_id`(10 by default) arguments to set the range of books to download.
```
python main.py --start_id --end_id
```
To parse fiction books category and download parsed books:
```
python parse_tululu_category.py --start_page --end_page --dest_folder --skip_imgs --skip_txt --json_path
```
- `--start_page` - first category page to get books from, `1` by default.

- `--end_page` - last category page to get books from, `4` by default.

- `--dest_folder` - destination folder to save json file with information on downloaded books, book texts and images.

- `--skip_imgs` - don't save book covers, `False` by default.

- `--skip_txt` - don't save book texts, `False` by default.

- `--json_path` - custom path to save json file with information on downloaded books.

### Project Goals

The code is written for educational purposes on online-course for web-developers [Devman](https://dvmn.org).