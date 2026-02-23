-- Dimension : Le type de carburant
CREATE TABLE dim_fuel (
    fuel_id SERIAL PRIMARY KEY,
    fuel_code VARCHAR(20) UNIQUE NOT NULL,
    fuel_name VARCHAR(50)
);

-- Dimension : La Station Service
CREATE TABLE dim_station (
    station_id SERIAL PRIMARY KEY,
    api_station_id VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6)
);

-- Dimension : Temps
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    month INT,
    day_of_week INT
);