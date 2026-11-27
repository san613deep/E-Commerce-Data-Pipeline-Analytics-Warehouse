# End-to-End E-Commerce Data Pipeline & Analytics Warehouse

A portfolio data-engineering project that generates synthetic e-commerce transactions, loads source CSVs into PostgreSQL staging tables, transforms them into a dimensional analytics warehouse, and orchestrates the workflow with Apache Airflow.

The repository demonstrates a local, reproducible batch-pipeline design. It is a learning/portfolio implementation, not a claim of production deployment.

## Business problem

Analytics teams need trustworthy sales, customer, product and order metrics. Raw transactional feeds can contain duplicates, missing values, invalid quantities and broken foreign-key references. This project makes those data-quality problems visible and applies explicit rules before data reaches the reporting model.

## Architecture

```text
Synthetic source generator
  ├── customers.csv
  ├── products.csv
  ├── orders.csv
  └── order_items.csv
          |
          v
  Source validation (CSV files and headers)
          |
          v
  PostgreSQL staging schema
          |
          v
  Data-quality checks and SQL transformations
          |
          v
  Analytics schema (dimensions + fact table)
          |
          v
  Reconciliation / quality views
          |
          v
  Power BI report
          
Apache Airflow orchestrates the pipeline tasks.
Docker Compose provides PostgreSQL and Airflow locally.
```

## Technology stack

| Area | Tools |
|---|---|
| Data generation and processing | Python, Pandas, NumPy |
| Database | PostgreSQL 16 |
| Orchestration | Apache Airflow 2.9.2 |
| Infrastructure | Docker Compose |
| Database access | Psycopg2 |
| Reporting | Power BI |

## Data and quality scenarios

The source generator creates synthetic records with a fixed random seed and deliberately injects quality issues for downstream validation.

| Source | Baseline / generated data | Injected issue |
|---|---:|---|
| Customers | 2,000 baseline rows | 15 duplicate rows and 15 missing cities |
| Products | 100 rows | 2 missing prices |
| Orders | 10,000 rows | 60 missing payment methods and 50 orphan customer IDs |
| Order items | Variable number of rows | 150 invalid quantities and 120 orphan product IDs |

The order-item count depends on the seeded sampling of 1–5 products per order. Run the generator to produce the exact count for the current implementation.

These are synthetic records; no customer personal data is used.

## Repository layout

```text
.
├── airflow/dags/
│   ├── ecommerce_etl.py
│   └── test_dag.py
├── dashboard/
│   ├── Ecommerce_Sales_Analytics.pbix
│   └── screenshots/
├── data/raw/                 # generated source CSVs
├── sql/                      # data-quality and reconciliation views
├── src/generate_data.py
├── tests/test_data_generation.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Run locally

### Prerequisites

- Python 3.11+
- Docker Desktop with Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/san613deep/E-Commerce-Data-Pipeline-Analytics-Warehouse.git
cd E-Commerce-Data-Pipeline-Analytics-Warehouse
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies and generate source data

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python src/generate_data.py
```

The generator writes four CSV files into `data/raw/`.

### 4. Run unit tests

The fast unit tests validate the synthetic data generator and injected anomaly counts. They do not require Airflow or PostgreSQL.

```bash
python -m pip install pandas numpy pytest
python -m pytest tests/ -q
```

### 5. Start the local services

```bash
docker compose up --build
```

The Compose file starts PostgreSQL and the Airflow initialization, webserver and scheduler services. Open Airflow at [http://localhost:8080](http://localhost:8080).

Use the credentials configured in your local Compose setup. Change all default credentials before exposing any service beyond localhost.

### 6. Run the pipeline

In the Airflow UI, locate the `ecommerce_etl` DAG and trigger it. Inspect task logs and the PostgreSQL staging/analytics schemas to verify each stage.

## Verification boundaries

- The GitHub Actions workflow runs the synthetic data-generator unit tests.
- The full ETL workflow requires Docker Compose, PostgreSQL and Airflow; it is not exercised by the lightweight unit-test job.
- Power BI report files are provided for inspection; refresh the report against your own local warehouse connection.
- Do not describe this project as production deployed or claim a successful end-to-end run unless you have personally run and verified that environment.

## Engineering decisions

- **Synthetic data:** makes the project reproducible without publishing real customer records.
- **Staging before transformation:** preserves source records for validation and replay.
- **Dimensional model:** separates descriptive dimensions from measurable sales facts.
- **Quality and reconciliation views:** make invalid records and source-to-warehouse differences inspectable.
- **Airflow orchestration:** makes task dependencies, retries and run history visible.

## Future improvements

- Add database-backed integration tests for staging loads and warehouse transformations.
- Add a disposable PostgreSQL service to CI and verify idempotent reruns.
- Add screenshots of the Power BI report and a reviewed architecture diagram.
- Parameterize local credentials and move all secrets to environment variables.
- Add data contracts and explicit schema-version handling.

## License

See the repository license file, if present, for reuse terms.
