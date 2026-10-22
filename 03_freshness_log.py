"""Codzienny log świeżości danych.

Sprawdza najstarszy i najnowszy rekord w tabelach źródłowych thelook_ecommerce
i DOPISUJE wynik do tabeli monitoring.data_freshness w naszym projekcie.
Uruchamiany automatycznie przez GitHub Actions (.github/workflows/freshness.yml),
ale można go też odpalić ręcznie:  python 03_freshness_log.py
"""
import pandas as pd
from google.cloud import bigquery

from bq_utils import client, run_query, DATASET, PROJECT_ID

TARGET_DATASET = f"{PROJECT_ID}.monitoring"
TARGET_TABLE = f"{TARGET_DATASET}.data_freshness"

DATED_TABLES = ["users", "orders", "order_items", "events", "inventory_items"]


def get_freshness() -> pd.DataFrame:
    """Jeden wiersz na tabelę: liczba wierszy, najstarszy i najnowszy rekord."""
    sql = "\nUNION ALL\n".join(
        f"SELECT '{t}' AS table_name, COUNT(*) AS row_count, "
        f"MIN(created_at) AS oldest, MAX(created_at) AS newest "
        f"FROM `{DATASET}.{t}`"
        for t in DATED_TABLES
    )
    df = run_query(sql)

    # Kiedy sprawdzaliśmy i jak "stare" są najnowsze dane
    df["checked_at"] = pd.Timestamp.now(tz="UTC")
    df["lag_minutes"] = (df["checked_at"] - df["newest"]).dt.total_seconds() / 60
    return df


def save(df: pd.DataFrame) -> None:
    """Tworzy zbiór danych (jeśli go nie ma) i dopisuje wiersze do tabeli logu."""
    # Lokalizacja US – ta sama co danych publicznych, żeby dało się je łączyć w jednym zapytaniu
    dataset = bigquery.Dataset(TARGET_DATASET)
    dataset.location = "US"
    client.create_dataset(dataset, exists_ok=True)

    # Load job z WRITE_APPEND: dopisuje nowe wiersze, nie nadpisuje historii.
    # Tabela powstanie sama przy pierwszym uruchomieniu (schemat z DataFrame).
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(df, TARGET_TABLE, job_config=job_config)
    job.result()  # czekamy, aż ładowanie się zakończy

    print(f"Dopisano {len(df)} wierszy do {TARGET_TABLE}")


if __name__ == "__main__":
    freshness = get_freshness()
    print(freshness.to_string(index=False))
    save(freshness)
