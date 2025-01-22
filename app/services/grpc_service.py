#app/services/grpc_service.py

import grpc
from .data_fetcher import get_google_books

def get_recommendations(genre=None):
    books = get_google_books(genre) if genre else get_google_books("")
    recommendations = sorted(books, key=lambda x: x.get('rating', 0), reverse=True)[:20]
    return recommendations