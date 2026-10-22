"""Wspólne ustawienia i funkcje do pracy z BigQuery. Importuj w każdym skrypcie:

    from bq_utils import client, run_query, DATASET
"""
from google.cloud import bigquery

PROJECT_ID = "thelook-analytics-512312"                  # Twój projekt GCP – to on "płaci" za zapytania
DATASET = "bigquery-public-data.thelook_ecommerce"       # źródło danych
MAX_BYTES = 1_000_000_000                                # bezpiecznik: zapytanie > 1 GB zostanie odrzucone

client = bigquery.Client(project=PROJECT_ID)


def run_query(sql: str, params: list | None = None, verbose: bool = True):
    """Szacuje koszt zapytania (dry run), a potem je wykonuje i zwraca DataFrame."""
    params = params or []

    # 1) Dry run – BigQuery liczy, ile danych przetworzy, ale niczego nie wykonuje (darmowe)
    dry = client.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            dry_run=True, use_query_cache=False, query_parameters=params
        ),
    )
    if verbose:
        print(f"Zapytanie przetworzy: {dry.total_bytes_processed / 1e6:.2f} MB")

    # 2) Właściwe wykonanie z limitem kosztu
    job = client.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=params, maximum_bytes_billed=MAX_BYTES
        ),
    )
    return job.to_dataframe()

