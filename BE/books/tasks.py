from datetime import datetime
from celery import shared_task

from books.models import Book
from books.crawlers.crawlers import AladinCrawler

@shared_task
def fetch_recent_book():
    print(f"Running task at {datetime.now()}")

    crawler = AladinCrawler()
    result = crawler.crawl()

    data = result.json()
    book_items = data['item']
    
    for book_data in book_items:
        title = book_data.get('title', '')
        author = book_data.get('author', '')
        publisher = book_data.get('publisher', None)
        detail_url = book_data.get('link', '')
        book_image = book_data.get('cover', '')
        published_date = book_data.get('pubDate', '')
        content = book_data.get('description', None)

        _, created = Book.objects.get_or_create(
            title=title,
            defaults={
                'author': author,
                'publisher': publisher,
                'detail_url': detail_url,
                'book_image': book_image,
                'published_date': published_date,
                'content': content,
            })
        
        if created:
            print(f"Add Book '{title}'")
        else:
            print(f"Skip Book '{title}' ")