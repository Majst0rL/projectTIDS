import requests

def get_top_books():
    url = "https://plus.cobiss.net/most-read-web/rest/v1/si/sl/books/search-public/?maxResult=100&periodFrom=202412&periodTo=202412&pubType=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        books = [
            {
                "title": book.get("title", "Unknown Title"),
                "author": book.get("author", "Unknown Author"),
                "genre": book.get("genre", "Unknown Genre"),
                "year": book.get("year", "Unknown Year"),
                "rating": book.get("rating", "N/A")
            }
            for book in data.get("results", [])
        ]
        return books
    return []

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