from celery import shared_task

from .pipeline import process_scraped_books
from .scraper import scrape_book_list


@shared_task
def scrape_books_task(pages: int = 5):
    scraped = scrape_book_list(max_pages=pages)
    return process_scraped_books(scraped)
