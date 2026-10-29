"""Tworzy lub aktualizuje widoki BigQuery z plików sql/views/*.sql w zbiorze `marts`.

Uruchomienie:  python deploy_views.py

* Nazwa widoku = nazwa pliku (np. sql/views/v_kpi_monthly.sql -> marts.v_kpi_monthly).
* CREATE OR REPLACE VIEW: ten sam skrypt tworzy widoki za pierwszym razem i aktualizuje je po zmianie SQL.
* Widok nie przechowuje danych – przy każdym odczycie (np. otwarciu dashboardu) liczy się na aktualnych
  danych źródłowych. Dlatego skrypt pokazuje, ile kosztuje jeden odczyt każdego widoku.
* Sandbox BigQuery: tabele i widoki we własnych zbiorach wygasają po 60 dniach – ponowne uruchomienie
  skryptu tworzy je od nowa.
"""
from pathlib import Path

from google.cloud import bigquery

from bq_utils import client, PROJECT_ID

DATASET_ID = f"{PROJECT_ID}.marts"
VIEWS_DIR = Path(__file__).parent / "sql" / "views"

# Same location as the public dataset (US) – views must live where their source tables are
dataset = bigquery.Dataset(DATASET_ID)
dataset.location = "US"
dataset.description = "Widoki KPI dla dashboardu TheLook (liczone na żywo z bigquery-public-data.thelook_ecommerce)"
client.create_dataset(dataset, exists_ok=True)
print(f"Zbiór: {DATASET_ID}")

for path in sorted(VIEWS_DIR.glob("*.sql")):
    view_id = f"{DATASET_ID}.{path.stem}"
    view_sql = path.read_text(encoding="utf-8")

    # Dry run first: validates the SQL and estimates the cost of one read (free)
    dry = client.query(view_sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))

    client.query(f"CREATE OR REPLACE VIEW `{view_id}` AS\n{view_sql}").result()
    print(f"  {path.stem:<22} OK   jeden odczyt: {dry.total_bytes_processed / 1e6:7.1f} MB")
