import hashlib
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from ast import literal_eval
from .utils import setup_logger
import re

logger = setup_logger(__name__)

def parse_point(point_str: str) -> tuple:
    """Extract coordinates from POINT string format"""
    coords = re.search(r'POINT \((.*?) (.*?)\)', point_str)
    if coords:
        return float(coords.group(1)), float(coords.group(2))
    raise ValueError(f"Invalid POINT format: {point_str}")

def ingest_csv(csv_path: str, db_url: str, batch_size: int = 10000):
    """
    Processes CSV data in chunks to handle large files:
    1. Reads CSV in configurable batches
    2. Parses geographic coordinates
    3. Generates unique trip IDs
    4. Bulk inserts into PostgreSQL
    5. Provides progress logging

    We will log all steps and progress to help with debugging and monitoring
    """
    logger.info(f"Starting ingestion from {csv_path}")
    
    total_rows = sum(1 for _ in open(csv_path)) - 1
    logger.info(f"Found {total_rows} records to process")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    total = 0
    chunk_num = 0
    start_time = pd.Timestamp.now()

    for chunk in pd.read_csv(csv_path, chunksize=batch_size):
        chunk_num += 1
        rows = []
        for _, row in chunk.iterrows():
            ox, oy = parse_point(row["origin_coord"])
            dx, dy = parse_point(row["destination_coord"])
            ts = row["datetime"]

            hash_id = generate_trip_hash(ox, oy, dx, dy, ts)

            rows.append((
                hash_id,
                row["region"],
                f"SRID=4326;POINT({ox} {oy})",
                f"SRID=4326;POINT({dx} {dy})",
                ts,
                row["datasource"]
            ))
        
        _bulk_insert(cur, rows)
        conn.commit()
        total += len(rows)
        
        progress = (total / total_rows) * 100
        logger.info(f"Progress: {progress:.1f}% - Chunk {chunk_num}: {len(rows)} records inserted (total: {total})")

    time_taken = pd.Timestamp.now() - start_time
    cur.close()
    conn.close()
    logger.info(f"Ingestion completed in {time_taken.total_seconds():.1f} seconds")
    logger.info(f"Final status: {total} records inserted successfully")


def _bulk_insert(cur, data):
    execute_values(cur, """
        INSERT INTO trips (id, city, origin, destination, ts, datasource)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """, data)


def generate_trip_hash(ox, oy, dx, dy, timestamp_str):
    """
    Generate a unique hash for the trip based on coordinates and timestamp,
    to group trips with similar origin, destination and time
    """
    ox_r = round(ox, 3)
    oy_r = round(oy, 3)
    dx_r = round(dx, 3)
    dy_r = round(dy, 3)

    hour = pd.to_datetime(timestamp_str).hour
    if 5 <= hour < 12:
        time_bin = "morning"
    elif 12 <= hour < 18:
        time_bin = "afternoon"
    elif 18 <= hour < 23:
        time_bin = "evening"
    else:
        time_bin = "night"

    base_str = f"{ox_r}_{oy_r}_{dx_r}_{dy_r}_{time_bin}"
    return hashlib.sha256(base_str.encode()).hexdigest()[:16]

def get_weekly_average(db_url: str, region: str = None, min_lon: float = None, 
                      min_lat: float = None, max_lon: float = None, max_lat: float = None):
    """Get weekly average number of trips by region or bounding box"""
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    if region:
        query = """
            SELECT 
                DATE_TRUNC('week', ts) as week,
                COUNT(*) as trip_count
            FROM trips 
            WHERE city = %s
            GROUP BY week
            ORDER BY week;
        """
        cur.execute(query, (region,))
    else:
        query = """
            SELECT 
                DATE_TRUNC('week', ts) as week,
                COUNT(*) as trip_count
            FROM trips 
            WHERE ST_Intersects(
                origin::geometry,
                ST_MakeEnvelope(%s, %s, %s, %s, 4326)
            )
            GROUP BY week
            ORDER BY week;
        """
        cur.execute(query, (min_lon, min_lat, max_lon, max_lat))

    results = cur.fetchall()
    
    if not results:
        logger.info("No trips found for the given criteria")
        return

    total_trips = sum(row[1] for row in results)
    num_weeks = len(results)
    average = total_trips / num_weeks

    logger.info(f"Weekly average trips: {average:.2f}")
    for week, count in results:
        logger.info(f"Week of {week.date()}: {count} trips")

    cur.close()
    conn.close()