#app/routes.py

import json
import re
import pandas as pd
from pyaxis import pyaxis
from flask import Blueprint, render_template, request, jsonify
from .services.data_fetcher import get_open_library_books, get_google_books
from .services.grpc_service import get_recommendations
from .services.event_bus import log_event
from .services.scraper import scrape_cobiss
from .services.data_store import (
    load_books_from_file, save_books_to_file,
    WORLD_DATA_FILE, SLOVENIA_DATA_FILE
)

MY_LIST_DATA_FILE = 'my_list.json'
PCAXIS_FILE = "H092S.PX"
OUTPUT_CSV = "parsed_data.csv"
METADATA_CSV = "metadata.csv"

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    """Fetch and display top books from the Open Library API."""
    books = get_open_library_books("top books")

    # Ensure consistent metadata
    for book in books:
        book['rating'] = book.get('rating', 'N/A')
        book['genre'] = book.get('genre', 'Unknown')
        book['author'] = book.get('author', 'Unknown')

    # Save books to the JSON file
    save_books_to_file(WORLD_DATA_FILE, books)

    # Log event
    log_event("Home page accessed - Top 100 Global Books")

    # Render the index page with the books
    return render_template('index.html', books=books)

@bp.route('/search')
def search_books():
    search_query = request.args.get('query', '')
    books = get_google_books(search_query)
    log_event(f"Search performed with query: {search_query}")
    return render_template('search.html', books=books, query=search_query)

@bp.route('/top100', methods=['GET'])
def top100():
    # Preberi predhodno shranjene podatke
    try:
        with open("scraped_books.json", "r", encoding="utf-8") as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []

    return render_template('top100.html', books=books)

@bp.route('/top100/scrape', methods=['POST'])
def scrape_and_update():
    books = scrape_cobiss()  # Sproži razčlenjevanje
    return jsonify({"message": "Scraping completed", "books": books}), 200
@bp.route('/recommendations')
def recommendations():
    genre_filter = request.args.get('genre', '')
    recommendations = get_recommendations(genre_filter)  # Call gRPC service for recommendations
    log_event(f"Recommendations retrieved for genre: {genre_filter}")
    return render_template('recommendations.html', books=recommendations, genre_filter=genre_filter)

@bp.route('/mylist', methods=['GET'])
def my_list():
    books = load_books_from_file(MY_LIST_DATA_FILE)
    return render_template('my_list.html', books=books)

@bp.route('/mylist', methods=['POST'])
def add_to_my_list():
    books = load_books_from_file(MY_LIST_DATA_FILE)
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data.get('title', 'Unknown Title'),
        "author": data.get('author', 'Unknown Author'),
        "genre": data.get('genre', 'Unknown Genre'),
        "year": data.get('year', 'Unknown Year'),
        "rating": data.get('rating', 'N/A')
    }
    books.append(new_book)
    save_books_to_file(MY_LIST_DATA_FILE, books)
    log_event(f"Book added to My List: {new_book['title']} by {new_book['author']}")
    return jsonify({"message": "Book added successfully"}), 201

@bp.route('/mylist/<int:book_id>', methods=['PUT'])
def update_my_list(book_id):
    books = load_books_from_file(MY_LIST_DATA_FILE)
    data = request.json
    for book in books:
        if book['id'] == book_id:
            book.update({
                "title": data.get('title', book['title']),
                "author": data.get('author', book['author']),
                "genre": data.get('genre', book['genre']),
                "year": data.get('year', book['year']),
                "rating": data.get('rating', book['rating'])
            })
            save_books_to_file(MY_LIST_DATA_FILE, books)
            log_event(f"Book updated in My List: {book['title']} by {book['author']}")
            return jsonify({"message": "Book updated successfully"}), 200
    return jsonify({"error": "Book not found"}), 404

@bp.route('/mylist/<int:book_id>', methods=['DELETE'])
def delete_from_my_list(book_id):
    books = load_books_from_file(MY_LIST_DATA_FILE)
    books = [book for book in books if book['id'] != book_id]
    save_books_to_file(MY_LIST_DATA_FILE, books)
    log_event(f"Book with ID {book_id} deleted from My List")
    return jsonify({"message": "Book deleted successfully"}), 200


@bp.route('/opendata')
def open_data():
    """Render the Open Data visualization page."""
    return render_template('open_data.html')

def parse_px_to_csv(file_path):
    """Parse PCAXIS file and save data and metadata to CSV."""
    try:
        parsed_data = pyaxis.parse(file_path, encoding="latin1")

        if "DATA" in parsed_data and isinstance(parsed_data["DATA"], pd.DataFrame):
            data_df = parsed_data["DATA"]
            metadata = parsed_data.get("METADATA", {})

            # Očisti imena stolpcev in jih popravi
            data_df.columns = [col.encode('latin1').decode('utf-8', errors='ignore') for col in data_df.columns]
            print("Imena stolpcev pred popravljanjem:", data_df.columns.tolist())

            # Preimenuj napačno interpretirane stolpce
            rename_mapping = {
                "RAVEN IZOBRAEVANJA": "RAVEN IZOBRAŽEVANJA",
            }
            data_df.rename(columns=rename_mapping, inplace=True)
            print("Imena stolpcev po popravljanju:", data_df.columns.tolist())

            # Preveri, če stolpec obstaja po preimenovanju
            if "RAVEN IZOBRAŽEVANJA" not in data_df.columns:
                raise ValueError(f"Stolpec 'RAVEN IZOBRAŽEVANJA' manjka tudi po preimenovanju. Na voljo so: {data_df.columns.tolist()}")

            # Shrani podatke in metapodatke
            data_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
            pd.DataFrame.from_dict(metadata, orient="index").to_csv(METADATA_CSV, header=False)

            return data_df, metadata
        else:
            print("Error: Parsed data is not in the expected format.")
            return None, None
    except Exception as e:
        print(f"Error parsing PCAXIS file: {e}")
        return None, None


@bp.route('/opendata/data', methods=['GET'])
def get_open_data():
    """Parse PCAXIS data and return for visualization."""
    try:
        data, metadata = parse_px_to_csv(PCAXIS_FILE)
        if data is None:
            return jsonify({"error": "Failed to parse PCAXIS data."}), 500

        # Popravi imena stolpcev
        data.columns = [col.strip().replace("", "Ž") for col in data.columns]

        # Pridobi unikatne vrednosti let in kategorij
        years = sorted(data["LETO"].unique())
        categories = data["RAVEN IZOBRAŽEVANJA"].unique()

        datasets = []
        for category in categories:
            filtered_data = data[data["RAVEN IZOBRAŽEVANJA"] == category]
            values = [filtered_data[filtered_data["LETO"] == year]["DATA"].iloc[0] if not filtered_data[filtered_data["LETO"] == year].empty else 0 for year in years]
            datasets.append({
                "label": category,
                "data": values,
                "borderColor": f"hsl({(hash(category) % 360)}, 70%, 50%)",
                "fill": False
            })

        return jsonify({
            "labels": years,
            "datasets": datasets
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
