from selenium.webdriver.edge.service import Service
from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
import json


def scrape_cobiss():
    driver_path = "C:\\Users\\majst\\Downloads\\edgedriver_win64\\msedgedriver.exe"  # Pravilna pot
    service = Service(driver_path)

    # Inicializirajte EdgeDriver
    driver = Edge(service=service)
    driver.get(
        "https://plus.cobiss.net/most-read-web/si/sl?utm_source=chatgpt.com#libAcronym&libType&periodFrom=202412&periodTo=202412&pubType=1&publishYear")

    driver.implicitly_wait(5)  # Počakajte, da se stran naloži

    books = []

    # Poiščite tabelo
    rows = driver.find_elements(By.CSS_SELECTOR, "#book-table tbody tr")
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 4:
            books.append({
                "title": columns[1].text.strip(),
                "author": columns[2].text.strip(),
                "loans": columns[3].text.strip()
            })

    driver.quit()

    # Shrani podatke v JSON
    with open("scraped_books.json", "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)

    return books
