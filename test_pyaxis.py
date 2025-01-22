from pyaxis import pyaxis
import pandas as pd

PCAXIS_FILE = "H092S.PX"
OUTPUT_CSV = "parsed_data.csv"

def parse_and_save_to_pandas(file_path):
    try:
        # Parsanje PCAXIS datoteke
        parsed_data = pyaxis.parse(file_path, encoding="latin1")

        # Preveri, če je rezultat DataFrame
        if isinstance(parsed_data, pd.DataFrame):
            # Shrani DataFrame kot CSV
            parsed_data.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
            print(f"Podatki so shranjeni kot CSV v {OUTPUT_CSV}")
            return parsed_data
        else:
            print("Nepodprta oblika podatkov:")
            print(parsed_data)
    except Exception as e:
        print(f"Napaka pri parsiranju PCAXIS datoteke: {e}")
        return None

if __name__ == "__main__":
    df = parse_and_save_to_pandas(PCAXIS_FILE)
    if df is not None:
        print("Prvih 5 vrstic podatkov:")
        print(df.head())  # Prikaže prvih 5 vrstic DataFrame
