import json
import os

WORLD_DATA_FILE = 'worldtop100.json'
SLOVENIA_DATA_FILE = 'slovenia_top100.json'

def load_books_from_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        return json.load(file)

def save_books_to_file(file_path, books):
    """Save books to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)
