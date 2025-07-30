# Default values for variables
DB_URL ?= postgresql://trip_user:trip_password@db:5432/trip_dataset
CSV_PATH ?= data/trips.csv
BATCH_SIZE ?= 10000
REGION ?= Prague
SQL_FILE ?= src/questions.sql

.PHONY: build up down ingest weekly-average clean

build:	# Build the Docker images
	docker compose build

up:	# Start the Docker containers
	docker compose up -d db

down: # Stop the Docker containers
	docker compose down

ingest:	# Ingest data from CSV into the database
	docker compose run --rm app main \
		--csv $(CSV_PATH) \
		--db $(DB_URL) \
		--batch_size $(BATCH_SIZE)

weekly-average:	# Calculate weekly average from the database
	docker compose run --rm app weekly-average \
		--db $(DB_URL) \
		--region $(REGION)

run-sql:	# Run SQL queries from a file against the database
	docker compose run --rm app run-sql \
		--db $(DB_URL) \
		--sql $(SQL_FILE)

clean:	# Clean up Docker containers and volumes
	docker compose down -v