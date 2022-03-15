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

### Project Goals

The code is written for educational purposes on online-course for web-developers [Devman](https://dvmn.org).