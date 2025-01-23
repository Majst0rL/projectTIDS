#app/routes.py
import datetime
import json
import re
import pandas as pd
from pyaxis import pyaxis
from flask import Blueprint, render_template, request, jsonify
from .services.data_fetcher import get_open_library_books, get_google_books
from .services.event_bus import publish_event
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
    """Fetch and display books from the Open Library API."""
    books = get_open_library_books("top books")

    for book in books:
        book['rating'] = book.get('rating', 'N/A')
        book['genre'] = book.get('genre', 'Unknown')
        book['author'] = book.get('author', 'Unknown')
    save_books_to_file(WORLD_DATA_FILE, books)

    # log_event("Home page accessed - Top 100 Global Books")

    return render_template('index.html', books=books)


@bp.route('/search')
def search_books():
    search_query = request.args.get('query', '')
    books = get_google_books(search_query)
    # log_event(f"Search performed with query: {search_query}")
    return render_template('search.html', books=books, query=search_query)


@bp.route('/top100', methods=['GET'])
def top100():
    try:
        with open("scraped_books.json", "r", encoding="utf-8") as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []

    return render_template('top100.html', books=books)


@bp.route('/top100/scrape', methods=['POST'])
def scrape_and_update():
    #Scraper
    books = scrape_cobiss()
    return jsonify({"message": "Scraping completed", "books": books}), 200


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

    # RabbitMQ event
    event_message = {
        "event": "BookAdded",
        "timestamp": datetime.datetime.now().isoformat(),
        "details": new_book
    }
    publish_event("user_actions", event_message)

    return jsonify({"message": "Book added successfully"}), 201


@bp.route('/mylist/<int:book_id>', methods=['PUT'])
def update_my_list(book_id):
    books = load_books_from_file(MY_LIST_DATA_FILE)
    data = request.json
    updated_book = None
    for book in books:
        if book['id'] == book_id:
            book.update({
                "title": data.get('title', book['title']),
                "author": data.get('author', book['author']),
                "genre": data.get('genre', book['genre']),
                "year": data.get('year', book['year']),
                "rating": data.get('rating', book['rating'])
            })
            updated_book = book
            break
    save_books_to_file(MY_LIST_DATA_FILE, books)

    # RabbitMQ event
    if updated_book:
        event_message = {
            "event": "BookUpdated",
            "timestamp": datetime.datetime.now().isoformat(),
            "details": updated_book
        }
        publish_event("user_actions", event_message)

    return jsonify({"message": "Book updated successfully"}), 200


@bp.route('/mylist/<int:book_id>', methods=['DELETE'])
def delete_from_my_list(book_id):
    books = load_books_from_file(MY_LIST_DATA_FILE)
    book_to_delete = next((book for book in books if book['id'] == book_id), None)
    books = [book for book in books if book['id'] != book_id]
    save_books_to_file(MY_LIST_DATA_FILE, books)

    # RabbitMQ event
    if book_to_delete:
        event_message = {
            "event": "BookDeleted",
            "timestamp": datetime.datetime.now().isoformat(),
            "details": book_to_delete
        }
        publish_event("user_actions", event_message)

    return jsonify({"message": "Book deleted successfully"}), 200


@bp.route('/opendata')
def open_data():
    return render_template('open_data.html')


def parse_px_to_csv(file_path):
    """Parse PCAXIS file and save data and metadata to CSV."""
    try:
        parsed_data = pyaxis.parse(file_path, encoding="latin1")

        if "DATA" in parsed_data and isinstance(parsed_data["DATA"], pd.DataFrame):
            data_df = parsed_data["DATA"]
            metadata = parsed_data.get("METADATA", {})

            data_df.columns = [col.encode('latin1').decode('utf-8', errors='ignore') for col in data_df.columns]
            print("Imena stolpcev pred popravljanjem:", data_df.columns.tolist())

            rename_mapping = {
                "RAVEN IZOBRAEVANJA": "RAVEN IZOBRAŽEVANJA",
            }
            data_df.rename(columns=rename_mapping, inplace=True)
            print("Imena stolpcev po popravljanju:", data_df.columns.tolist())

            if "RAVEN IZOBRAŽEVANJA" not in data_df.columns:
                raise ValueError(
                    f"Stolpec 'RAVEN IZOBRAŽEVANJA' manjka tudi po preimenovanju. Na voljo so: {data_df.columns.tolist()}")

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

        data.columns = [col.strip().replace("", "Ž") for col in data.columns]

        years = sorted(data["LETO"].unique())
        categories = data["RAVEN IZOBRAŽEVANJA"].unique()

        datasets = []
        for category in categories:
            filtered_data = data[data["RAVEN IZOBRAŽEVANJA"] == category]
            values = [filtered_data[filtered_data["LETO"] == year]["DATA"].iloc[0] if not filtered_data[
                filtered_data["LETO"] == year].empty else 0 for year in years]
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
