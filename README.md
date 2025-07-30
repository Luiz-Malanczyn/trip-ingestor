# Trip Data Ingestion Service

A scalable service for ingesting and analyzing trip data with support for geographic queries.

## Features

- CSV data ingestion with batch processing
- Geographic data handling with PostGIS
- Weekly average trip calculations by region or bounding box
- Custom SQL query execution
- Containerized deployment with Docker
- Scalable to handle large datasets

## Requirements

- Docker and Docker Compose
- Make (optional, for using Makefile commands)
- PostgreSQL client (optional, for direct database access)

## Quick Start

1. Build the containers:
```sh
make build
```

2. Start the database:
```sh
make up
```

3. Ingest trip data:
```sh
make ingest CSV_PATH=data/trips.csv BATCH_SIZE=10000
```

4. Get weekly averages:
```sh
# By region
make weekly-average REGION=Prague

# By bounding box
make weekly-average \
  min_lon=14.3 min_lat=50.0 \
  max_lon=14.6 max_lat=50.2
```

5. Run custom SQL queries:
```sh
make run-sql SQL_FILE=src/question1.sql
```

## Project Structure

```
trip-ingestor/
├── data/              # Data files
│   └── trips.csv     # Sample trip data
├── src/              # Source code
│   ├── ingest.py    # Core ingestion logic
│   ├── main.py      # CLI interface
│   └── utils.py     # Utility functions
├── dbschema.sql     # Database schema
├── docker-compose.yml
├── Dockerfile
└── Makefile
```

## Data Model

```sql
CREATE TABLE trips (
  id TEXT PRIMARY KEY,           -- Unique trip identifier
  city TEXT,                     -- Region/city name
  origin GEOGRAPHY(POINT, 4326), -- Trip start location
  destination GEOGRAPHY(POINT, 4326), -- Trip end location
  ts TIMESTAMP NOT NULL,         -- Trip timestamp
  datasource TEXT,              -- Data provider
  ingested_at TIMESTAMP DEFAULT now()
);
```

## Scalability Features

- Chunk-based CSV processing
- Batch database inserts
- PostgreSQL spatial indexing
- Docker containerization
- Configurable batch sizes
- Geographic query optimization

## Development

### Environment Setup

1. Clone the repository:
```sh
git clone https://github.com/yourusername/trip-ingestor.git
cd trip-ingestor
```

2. Build the development environment:
```sh
make build
```

### Database Access

Connect to PostgreSQL:
```sh
psql postgresql://trip_user:trip_password@localhost:5432/trip_dataset
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DB_URL | Database connection URL | postgresql://trip_user:trip_password@db:5432/trip_dataset |
| CSV_PATH | Path to input CSV file | data/trips.csv |
| BATCH_SIZE | Number of records per batch | 10000 |
| REGION | Region name for analytics | Prague |
| SQL_FILE | Path to SQL query file | src/questions.sql |


## Cloud Architecture Sketch

This solution can be deployed to cloud providers using the following architecture:

### AWS Components
- **Storage**: S3 for data lake
- **Processing**: AWS Glue with Spark
- **Streaming**: MSK (Managed Kafka)
- **Orchestration**: Step Functions
- **Database**: RDS PostgreSQL with PostGIS
- **Monitoring**: CloudWatch

### Key Implementation Points
1. **Batch Processing**
   - AWS Glue Crawlers scan S3 data
   - Glue ETL jobs using Spark
   - Dynamic Frame transformations
   - JDBC bulk loading to PostgreSQL

2. **Real-time Processing**
   - Kafka topics for trip events
   - Kafka Connect for PostgreSQL sync
   - Glue Streaming ETL jobs
   - Near real-time analytics

3. **Orchestration**
   - Step Functions manage workflow
   - Error handling and retries
   - Conditional processing paths
   - Job monitoring and alerts

4. **Monitoring & Scaling**
   - Glue job metrics
   - MSK performance monitoring
   - Auto-scaling policies
   - CloudWatch dashboards