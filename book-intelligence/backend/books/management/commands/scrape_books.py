from django.core.management.base import BaseCommand

from books.pipeline import process_scraped_books
from books.scraper import scrape_book_list


class Command(BaseCommand):
    help = "Scrape books from books.toscrape.com and process them through AI + vector pipeline"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=5, help="Number of catalogue pages to scrape")

    def handle(self, *args, **options):
        pages = options["pages"]
        self.stdout.write(self.style.NOTICE(f"Scraping {pages} pages..."))

        books = scrape_book_list(max_pages=pages)
        if not books:
            self.stdout.write(self.style.WARNING("No books scraped."))
            return

        result = process_scraped_books(books)
        self.stdout.write(self.style.SUCCESS(f"Processed: {result['total_processed']}"))
        self.stdout.write(self.style.SUCCESS(f"Created: {result['created']}"))
        self.stdout.write(self.style.SUCCESS(f"Updated: {result['updated']}"))

        if result["errors"]:
            self.stdout.write(self.style.WARNING(f"Errors: {len(result['errors'])}"))
            for err in result["errors"][:10]:
                self.stdout.write(f" - {err}")
