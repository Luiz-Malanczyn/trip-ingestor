import typer
import psycopg2
from pathlib import Path
from .ingest import ingest_csv, get_weekly_average

app = typer.Typer()

@app.command()
def main(
    csv_path: str = typer.Option(..., "--csv", help="Path to CSV file"),
    db_url: str = typer.Option(..., "--db", help="Database URL"),
    batch_size: int = typer.Option(..., "--batch_size", help="Bastch size for ingestion")
):
    """
    Ingest trip data from CSV into PostgreSQL database
    """
    ingest_csv(csv_path, db_url, batch_size)


@app.command()
def weekly_average(
    db_url: str = typer.Option(..., "--db", help="Database URL"),
    region: str = typer.Option(None, "--region", help="Region name (e.g. Prague)"),
    min_lon: float = typer.Option(None, "--min-lon", help="Minimum longitude for bounding box"),
    min_lat: float = typer.Option(None, "--min-lat", help="Minimum latitude for bounding box"),
    max_lon: float = typer.Option(None, "--max-lon", help="Maximum longitude for bounding box"),
    max_lat: float = typer.Option(None, "--max-lat", help="Maximum latitude for bounding box"),
):
    """
    Get weekly average number of trips for a region or bounding box
    """
    get_weekly_average(db_url, region, min_lon, min_lat, max_lon, max_lat)

@app.command()
def run_sql(
    db_url: str = typer.Option(..., "--db", help="Database URL"),
    sql_file: Path = typer.Option(..., "--sql", help="Path to SQL file"),
):
    """
    Execute SQL queries from a file
    """
    sql_content = sql_file.read_text()
    
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)
            
            try:
                results = cur.fetchall()
                if results:
                    columns = [desc[0] for desc in cur.description]
                    print("\t".join(columns))
                    print("-" * 80)
                    
                    for row in results:
                        print("\t".join(str(cell) for cell in row))
            except psycopg2.ProgrammingError:
                pass
            
            conn.commit()

if __name__ == "__main__":
    app()