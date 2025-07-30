CREATE TABLE trips (
  id TEXT PRIMARY KEY,           -- Unique trip identifier
  city TEXT,                     -- Region/city name
  origin GEOGRAPHY(POINT, 4326), -- Trip start location
  destination GEOGRAPHY(POINT, 4326), -- Trip end location
  ts TIMESTAMP NOT NULL,         -- Trip timestamp
  datasource TEXT,              -- Data provider
  ingested_at TIMESTAMP DEFAULT now() -- Ingestion timestamp
);