import requests

def get_google_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": item['volumeInfo'].get('title', 'N/A'),
                "author": ', '.join(item['volumeInfo'].get('authors', ['Unknown'])),
                "genre": ', '.join(item['volumeInfo'].get('categories', ['Unknown'])),
                "year": item['volumeInfo'].get('publishedDate', 'N/A')[:4],
                "rating": item['volumeInfo'].get('averageRating', 'N/A')
            }
            for item in data.get('items', [])
        ]
    return []

def get_open_library_books(query):
    url = f"https://openlibrary.org/search.json?q={query}&limit=40"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": book.get('title', 'N/A'),
                "author": ', '.join(book.get('author_name', ['Unknown'])),
                # Extract only the first genre if available
                "genre": book.get('subject', ['Unknown'])[0] if book.get('subject') else 'Unknown',
                "year": book.get('first_publish_year', 'N/A'),
                "rating": "N/A"  # Open Library does not provide ratings
            }
            for book in data.get('docs', [])
        ]
    return []