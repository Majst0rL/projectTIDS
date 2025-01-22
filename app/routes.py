from flask import Blueprint, render_template, request
from .services.data_fetcher import get_top_books, get_google_books
from .services.grpc_service import get_recommendations
from .services.event_bus import log_event

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    books = get_top_books()  # Fetch top 100 books
    log_event("Home page accessed")
    return render_template('index.html', books=books)  # Pass books to the template

@bp.route('/search')
def search_books():
    search_query = request.args.get('query', '')
    books = get_google_books(search_query)
    log_event(f"Search performed with query: {search_query}")
    return render_template('search.html', books=books, query=search_query)

@bp.route('/top100')
def top100():
    genre_filter = request.args.get('genre', '')
    books = get_top_books()
    if genre_filter:
        books = [book for book in books if genre_filter.lower() in book['genre'].lower()]
    log_event("Filtered top 100 books retrieved")
    return render_template('top100.html', books=books, genre_filter=genre_filter)

@bp.route('/recommendations')
def recommendations():
    genre_filter = request.args.get('genre', '')
    recommendations = get_recommendations(genre_filter)  # Call gRPC service for recommendations
    log_event(f"Recommendations retrieved for genre: {genre_filter}")
    return render_template('recommendations.html', books=recommendations, genre_filter=genre_filter)