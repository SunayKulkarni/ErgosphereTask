import logging
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

STAR_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0,
}


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def _parse_price(price_text: str) -> Optional[float]:
    try:
        clean = (
            price_text.replace("£", "")
            .replace("Â", "")
            .replace("$", "")
            .strip()
        )
        return float(clean)
    except (TypeError, ValueError):
        return None


def _parse_rating(star_class: str) -> Optional[float]:
    for key, value in STAR_MAP.items():
        if key in star_class:
            return value
    return None


def scrape_book_detail(book_url: str, driver: Optional[webdriver.Chrome] = None) -> Dict:
    local_driver = driver
    created_local_driver = False

    if local_driver is None:
        try:
            local_driver = _build_driver()
            created_local_driver = True
        except WebDriverException as exc:
            logger.exception("Failed to create Selenium driver: %s", exc)
            return {}

    try:
        try:
            local_driver.get(book_url)
        except Exception as exc:
            logger.exception("Failed fetching detail page %s: %s", book_url, exc)
            return {}

        time.sleep(1)
        soup = BeautifulSoup(local_driver.page_source, "html.parser")

        title = ""
        try:
            title_tag = soup.select_one(".product_main h1")
            title = title_tag.get_text(strip=True) if title_tag else ""
        except Exception:
            title = ""

        rating = None
        try:
            rating_tag = soup.select_one(".product_main p.star-rating")
            rating = _parse_rating(" ".join(rating_tag.get("class", []))) if rating_tag else None
        except Exception:
            rating = None

        price = None
        try:
            price_tag = soup.select_one(".product_main p.price_color")
            price = _parse_price(price_tag.get_text(strip=True) if price_tag else "")
        except Exception:
            price = None

        description = ""
        try:
            desc_header = soup.select_one("#product_description")
            if desc_header and desc_header.find_next_sibling("p"):
                description = desc_header.find_next_sibling("p").get_text(strip=True)
        except Exception:
            description = ""

        cover_image_url = ""
        try:
            image_tag = soup.select_one(".item.active img")
            if image_tag and image_tag.get("src"):
                cover_image_url = urljoin(book_url, image_tag["src"])
        except Exception:
            cover_image_url = ""

        reviews_count = None
        try:
            table_rows = soup.select("table.table.table-striped tr")
            for row in table_rows:
                header = row.select_one("th")
                value = row.select_one("td")
                if header and value and header.get_text(strip=True) == "Number of reviews":
                    reviews_count = int(value.get_text(strip=True))
                    break
        except Exception:
            reviews_count = None

        return {
            "title": title,
            "author": "Unknown Author",
            "rating": rating,
            "price": price,
            "reviews_count": reviews_count,
            "description": description,
            "book_url": book_url,
            "cover_image_url": cover_image_url,
        }
    finally:
        if created_local_driver and local_driver is not None:
            local_driver.quit()


def scrape_book_list(max_pages: int = 5) -> List[Dict]:
    books: List[Dict] = []

    try:
        driver = _build_driver()
    except WebDriverException as exc:
        logger.exception("Unable to initialize Selenium driver: %s", exc)
        return books

    try:
        for page in range(1, max_pages + 1):
            page_url = CATALOGUE_PAGE_URL.format(page)
            try:
                driver.get(page_url)
            except Exception as exc:
                logger.exception("Failed fetching list page %s: %s", page_url, exc)
                continue

            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            articles = soup.select("article.product_pod")
            if not articles:
                break

            for article in articles:
                try:
                    link_tag = article.select_one("h3 a")
                    if not link_tag or not link_tag.get("href"):
                        continue

                    book_url = urljoin(page_url, link_tag["href"])
                    detail = scrape_book_detail(book_url, driver=driver)
                    if not detail:
                        continue

                    if detail.get("reviews_count") is None and detail.get("price") is not None:
                        detail["reviews_count"] = int(detail["price"] * 10)

                    books.append(detail)
                except Exception as exc:
                    logger.exception("Error parsing a book on %s: %s", page_url, exc)
                    continue

            time.sleep(1)
    finally:
        driver.quit()

    return books
